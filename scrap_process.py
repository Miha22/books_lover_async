import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
import asyncio
import logging
from multiprocessing.queues import Queue
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_page(semaphore, session, id: int):
    url = f"https://breadl.org/d/{id}"
    retry_options = ExponentialRetry(attempts=2, start_timeout=3)
    retry_client = RetryClient(session, retry_options=retry_options)

    try:
        async with semaphore:
            async with retry_client.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"}) as response:#to avoid ban, hopefully
                if response.status != 200:
                    logger.warning(f"Error {response.status}: {url}")
                    return None

                page_content = await response.text()
                tree = html.fromstring(page_content)

                #h1 from div.card-header
                h1_text = tree.xpath("//div[@class='card-header']/h1/text()")
                h1_text = h1_text[0].strip() if h1_text else ""

                #href from <a id='start_download'> in div.mt-2
                start_download_link = tree.xpath("//div[@class='mt-2']/a[@id='start_download']/@href")
                start_download_link = start_download_link[0] if start_download_link else ""

                #href from <a id='mirror1'> in div#mirrors
                mirror1_link = tree.xpath("//div[@id='mirrors']/a[@id='mirror1']/@href")
                mirror1_link = mirror1_link[0] if mirror1_link else ""

                #<a> in div.mt-3 (next to #mirrors)
                tor_link = ""
                mirrors_div = tree.xpath("//div[@id='mirrors']")
                if mirrors_div:
                    next_div = mirrors_div[0].getnext() 
                    if next_div is not None and next_div.attrib.get("class") == "mt-3":
                        tor_tags = next_div.xpath(".//a[@class='btn bg-black text-white download_now']/@href")
                        tor_link = tor_tags[-1] if tor_tags else ""

                return f"{url}\n{h1_text}\n{start_download_link}\n{mirror1_link}\n{tor_link}\n\n"

    except Exception as e:
        logger.exception(f"Exception fetching {url}: {e}")
        return None

async def fetch_data(start_id: int, length: int, concurrency: int, queue: Queue):
    semaphore = asyncio.Semaphore(concurrency)
    tasks = []

    async with aiohttp.ClientSession() as session:
        for id in range(start_id, start_id + length):
            tasks.append(scrape_page(semaphore, session, id))

            if len(tasks) == concurrency:
                results = await asyncio.gather(*tasks)
                for r in results:
                    if r:
                        queue.put(r)#sending extracted links+name to the file writer process
                tasks.clear()
        if tasks:
            results = await asyncio.gather(*tasks)
            for r in results:
                if r:
                    queue.put(r)