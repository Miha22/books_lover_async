import multiprocessing
import asyncio
import aiofiles
import time
from scrap_process import fetch_data

def run_async_process(start_index: int, length: int, total_length: int, id_ttl: int, concurrency: int, queue: multiprocessing.Queue, timeout_counter, ready_counter):
    asyncio.run(fetch_data(list(range(start_index, start_index + length)), total_length, id_ttl, concurrency, queue, timeout_counter, ready_counter))

async def async_file_writer(queue: multiprocessing.Queue, buffer_size: int, out_file: str):
    buffer = []

    async with aiofiles.open(out_file, "w", encoding="utf-8") as f:
        while True:
            data = await asyncio.to_thread(queue.get)
            if data is None:
                break

            buffer.append(data)

            if len(buffer) >= buffer_size:
                await f.write(''.join(buffer))
                buffer.clear()

        if buffer:
            await f.write(''.join(buffer))

def file_writer(queue: multiprocessing.Queue, buffer_size: int, out_file: str):
    asyncio.run(async_file_writer(queue, buffer_size, out_file))        

def launch(proc_num: int, concurrency: int, buffer_size: int, out_file: str, start_id: int, end_id: int, id_ttl: int):
    start_time = time.time()
    total_length = end_id - start_id + 1
    chunk_size = total_length // proc_num
    chunk_size_last = end_id - start_id + 1 - chunk_size * proc_num + chunk_size

    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()
    writer_process = multiprocessing.Process(target=file_writer, args=(queue, buffer_size, out_file))
    writer_process.start()

    processes = []
    timeout_counters = []
    ready_counter = multiprocessing.Value('I', 0)#progress

    for i in range(proc_num):
        timeout_counter = multiprocessing.Value('I', 0)#to sum up total timeouts later
        timeout_counters.append(timeout_counter)
        processes.append(multiprocessing.Process(
            target=run_async_process, 
            args=(i * chunk_size + start_id,
                  chunk_size_last if i == proc_num - 1 else chunk_size, total_length, id_ttl,
                  concurrency, queue, timeout_counter, ready_counter)
        ))
    
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    end_time = time.time()
    for _ in range(proc_num):
        queue.put(None)
    execution_time = end_time - start_time
    total_requests = end_id - start_id + 1
    timeouts = sum(tc.value for tc in timeout_counters)
    loss_percentage = (timeouts / total_requests) * 100

    return (timeouts, loss_percentage, execution_time, (total_requests - timeouts) / execution_time)

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    elif sys.platform != "win32":
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPOlicy())
    #figure out better way for platform detection    
    start_id = 6
    end_id = 1403112
    proc_num = 4
    concurrency = 10
    buffer_size = 50000

    if len(sys.argv) != 6:
        print("Usage: python app.py <start index> <end index> <number of processes> <conrurrent connections>\nProceeding with default parameters: (6) (1403112) (4) (10) (50000)")

    start_id = int(sys.argv[1])
    end_id = int(sys.argv[2])
    proc_num = int(sys.argv[3])
    concurrency = int(sys.argv[4])
    buffer_size = int(sys.argv[5])
    out_file = f"out/books_{start_id}_{end_id}_{proc_num}_{concurrency}_{end_id - start_id + 1}.txt"

    if any(x < 0 for x in (start_id, end_id, proc_num, concurrency, buffer_size)):
        print("Invalid parameter(-s): Negative value(-s) entered")
        sys.exit(1)
    launch(proc_num, concurrency, buffer_size, out_file, start_id, end_id)