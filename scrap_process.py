import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
import asyncio
import logging
import random
import multiprocessing
import time
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
failed_ids = asyncio.Queue()
timeouts_local = 0

async def scrape_page(semaphore, session, retry_client, id: int, timeout_counter):
    global timeouts_local
    url = f"https://breadl.org/d/{id}"
    try:
        async with semaphore:
            await asyncio.sleep(random.uniform(0, 0.5))
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9"
            }
            async with retry_client.get(url, timeout=10, headers=headers) as response:
                if response.status != 200:
                    #logger.warning(f"Error {response.status}: {url}")
                    return None

                page_content = await response.text()
                tree = html.fromstring(page_content)

                h1_text = tree.xpath("//div[@class='card-header']/h1/text()")
                h1_text = h1_text[0].strip() if h1_text else ""

                start_download_link = tree.xpath("//div[@class='mt-2']/a[@id='start_download']/@href")
                start_download_link = start_download_link[0] if start_download_link else ""

                mirror1_link = tree.xpath("//div[@id='mirrors']/a[@id='mirror1']/@href")
                mirror1_link = mirror1_link[0] if mirror1_link else ""

                tor_link = ""
                mirrors_div = tree.xpath("//div[@id='mirrors']")
                if mirrors_div:
                    next_div = mirrors_div[0].getnext()
                    if next_div is not None and next_div.attrib.get("class") == "mt-3":
                        tor_tags = next_div.xpath(".//a[@class='btn bg-black text-white download_now']/@href")
                        tor_link = tor_tags[-1] if tor_tags else ""

                return f"{url}\n{h1_text}\n{start_download_link}\n{mirror1_link}\n{tor_link}\n\n"

    except asyncio.exceptions.CancelledError:
        #logging.error(f"Request cancelled: {url}")
        return None

    except asyncio.TimeoutError:
        await failed_ids.put(id)
        #timeouts_local += 1
        with timeout_counter.get_lock():
            timeout_counter.value += 1
        #logger.error(f"Timeout id {id}\nURL {url}\n")
        return None

    except Exception as e:
        #logger.error(f"Exception fetching {url}: {e}")
        return None

async def get_semaphore(concurrency: int, timeout_counter):
    if timeout_counter.value > 10:
        concurrency = max(1, concurrency // 2)
    elif timeout_counter.value == 0:
        concurrency = min(50, concurrency + 5)
    return asyncio.Semaphore(concurrency)


async def fetch_data(ids: list, total_length: int, ttl: int, concurrency: int, queue: multiprocessing.Queue, timeout_counter, ready_counter):
    if ttl < 1:
        return
    semaphore_levels = [
        asyncio.Semaphore(5),
        asyncio.Semaphore(concurrency // 2),
        asyncio.Semaphore(concurrency),
        asyncio.Semaphore(int(concurrency * 1.1)),
        asyncio.Semaphore(int(concurrency * 1.2)),
        asyncio.Semaphore(int(concurrency * 1.3)),
        asyncio.Semaphore(int(concurrency * 1.5)),
        asyncio.Semaphore(int(concurrency * 2))
    ]

    tasks = []
    timeout_velocity = 0
    timeouts_prev = timeout_counter.value
    speed = int((len(semaphore_levels) // 2) - 1)
    speed_alter_attempts = len(semaphore_levels) - 3
    # if not semaphore_levels:
    #     raise ValueError("semaphore_levels is empty! ")
    start_time = time.time()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50, ssl=False)) as session:
        retry_options = ExponentialRetry(attempts=5, start_timeout=2)
        retry_client = RetryClient(session, retry_options=retry_options)
        temp_failed = 0
        for id in ids:
            timeout_velocity = timeout_counter.value - timeouts_prev
            timeouts_prev = timeout_counter.value

            if timeout_velocity > 0:
                speed = max(0, speed - 2)
                #logger.info(f"Speed adjusted to {speed}, attempts left: {speed_alter_attempts}")
            else:
                if speed_alter_attempts > 0 and speed < len(semaphore_levels) - 1:
                    speed += 1
                    #logger.info(f"Speed adjusted to {speed}, attempts left: {speed_alter_attempts}")

            # if speed < 0 or speed >= len(semaphore_levels):
            #     logger.error(f"Invalid speed index: {speed}, valid range: 0-{len(semaphore_levels) - 1}")
            #     speed = max(0, min(len(semaphore_levels) - 1, speed))

            semaphore = semaphore_levels[speed]
            tasks.append(asyncio.create_task(scrape_page(semaphore, session, retry_client, id, timeout_counter)))

            if len(tasks) == concurrency:
                timeout_velocity = timeout_counter.value - timeouts_prev
                timeouts_prev = timeout_counter.value
                #start_time = time.time()
                results = await asyncio.gather(*tasks)
                #end_time = time.time()
                for r in results:
                    if r:
                        queue.put_nowait(r)   
                #execution_time = end_time - start_time
                processed = concurrency - (failed_ids.qsize() - temp_failed)
                with ready_counter.get_lock():  
                    ready_counter.value += processed
                    ready = ready_counter.value
                elapsed_time = time.time() - start_time
                recorded_speed = ready / elapsed_time if elapsed_time > 0 else 0
                remaining_books = total_length - ready
                eta = remaining_books / recorded_speed if recorded_speed > 0 else float('inf')

                logger.info(f"Processed books: {ready}/{total_length} total\n"
                            f"Progress: ({ready / total_length * 100:.2f}%)\n"
                            f"Speed: {recorded_speed:.2f} books/sec\n"
                            f"Estimated time remaining: {eta // 3600}(h.) {(eta % 3600) // 60}(min.) {eta % 60:.0f}(sec.)\n")
                tasks.clear()
                
        if tasks:
            results = await asyncio.gather(*tasks)
            for r in results:
                if r:
                    queue.put_nowait(r)

    failed_to_retry = []
    while not failed_ids.empty():
        failed_to_retry.append(await failed_ids.get())
    with timeout_counter.get_lock():
        timeout_counter.value -= len(failed_to_retry)
    
    if failed_to_retry:
        #await asyncio.sleep(3)
        await fetch_data(failed_to_retry, total_length, ttl - 1, concurrency, queue, timeout_counter, ready_counter)

# if timeouts_local > 0:
#     with timeout_counter.get_lock():
#         timeout_counter.value += timeouts_local
#     timeouts_local = 0

# while not failed_ids.empty():
#     id_to_retry = failed_ids.get()
#     print(f"Retrying {id_to_retry}...")

# def store_failed_id(id):
#     with open("failed_ids.txt", "a") as f:
#         f.write(f"{id}\n")  # Append ID to file

# with open("failed_ids.txt", "r") as f:
#     failed_ids = [int(line.strip()) for line in f]