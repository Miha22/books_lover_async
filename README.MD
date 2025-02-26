# Books_lover_async
Session based web scrapper for obtaining books by direct links + mirrors + tor without cooldown. Text file gets generated with book name, direct link, mirror link, tor link. Around 255Kb per 1000 books, so around 360MB for 1.4 million books in a text file format.
```python
...
return f"
    {url}\n
    {h1_text}\n
    {start_download_link}\n
    {mirror1_link}\n
    {tor_link}\n\n"
```
Example output from libgen_books_and_mirrors.txt

```
https://breadl.org/d/83
JavaScript: The Comprehensive Guide to Learning Professional JavaScript Programming
https://download.books.ms/main/3376000/dd0be4a958c084b281b48cb7bb556911/Philip%20Ackermann%20-%20JavaScript_%20The%20Comprehensive%20Guide%20to%20Learning%20Professional%20JavaScript%20Programming-Rheinwerk%20Computing%20%282022%29(Z-Lib.io).pdf
http://176.119.25.72/main/3376000/dd0be4a958c084b281b48cb7bb556911/Philip%20Ackermann%20-%20JavaScript_%20The%20Comprehensive%20Guide%20to%20Learning%20Professional%20JavaScript%20Programming-Rheinwerk%20Computing%20%282022%29(Z-Lib.io).pdf
http://libgenfrialc7tguyjywa36vtrdcplwpxaw43h6o63dmmwhvavo5rqqd.onion/LG/03376000/dd0be4a958c084b281b48cb7bb556911/Philip%20Ackermann%20-%20JavaScript_%20The%20Comprehensive%20Guide%20to%20Learning%20Professional%20JavaScript%20Programming-Rheinwerk%20Computing%20%282022%29(Z-Lib.io).pdf

https://breadl.org/d/84
Value Stream Mapping: How to Visualize Work and Align Leadership for Organizational Transformation
https://download.books.ms/main/3296000/39035ed8a575ff538c535030b83b5bc1/Karen%20%20%20Martin%2C%20Mike%20Osterling%20-%20Value%20Stream%20Mapping_%20How%20to%20Visualize%20Work%20and%20Align%20Leadership%20for%20Organizational%20Transformation-McGraw-Hill%20%282013%29(Z-Lib.io).epub
http://176.119.25.72/main/3296000/39035ed8a575ff538c535030b83b5bc1/Karen%20%20%20Martin%2C%20Mike%20Osterling%20-%20Value%20Stream%20Mapping_%20How%20to%20Visualize%20Work%20and%20Align%20Leadership%20for%20Organizational%20Transformation-McGraw-Hill%20%282013%29(Z-Lib.io).epub
http://libgenfrialc7tguyjywa36vtrdcplwpxaw43h6o63dmmwhvavo5rqqd.onion/LG/03296000/39035ed8a575ff538c535030b83b5bc1/Karen%20%20%20Martin%2C%20Mike%20Osterling%20-%20Value%20Stream%20Mapping_%20How%20to%20Visualize%20Work%20and%20Align%20Leadership%20for%20Organizational%20Transformation-McGraw-Hill%20%282013%29(Z-Lib.io).epub

https://breadl.org/d/85
Value Stream Mapping: Using Lean Business Practices to Transform Office and Service Environments
https://download.books.ms/main/3439000/074aa175fdb8f3ece6b7c8749df84de6/Karen%20Martin_%20Mike%20Osterling%20-%20Value%20Stream%20Mapping_%20Using%20Lean%20Business%20Practices%20to%20Transform%20Office%20and%20Service%20Environments-McGraw-Hill%20%282013%29(Z-Lib.io).epub
http://176.119.25.72/main/3439000/074aa175fdb8f3ece6b7c8749df84de6/Karen%20Martin_%20Mike%20Osterling%20-%20Value%20Stream%20Mapping_%20Using%20Lean%20Business%20Practices%20to%20Transform%20Office%20and%20Service%20Environments-McGraw-Hill%20%282013%29(Z-Lib.io).epub
http://libgenfrialc7tguyjywa36vtrdcplwpxaw43h6o63dmmwhvavo5rqqd.onion/LG/03439000/074aa175fdb8f3ece6b7c8749df84de6/Karen%20Martin_%20Mike%20Osterling%20-%20Value%20Stream%20Mapping_%20Using%20Lean%20Business%20Practices%20to%20Transform%20Office%20and%20Service%20Environments-McGraw-Hill%20%282013%29(Z-Lib.io).epub

```
## Suggestions
1. Increase number of simulataneous tcp connections
    win cmd: netsh int ipv4 set dynamicport tcp start=1024 num=64511
2. Switch ProactorEventLoop to **uvloop (linux)** or **SelectorEventLoop** in **Win32**, because it is limited
3. use asyncs wherever possible, semaphore = asyncio.Semaphore(500), adjust to test simultaneous connections
    The windows Proactor crashed after 10K simultaneous tcp connections showing Socket Resource Exhaustion, Overlapping Async Operations.
    For example:
    "OSError: [WinError 10038] An operation was attempted on something that is not a socket"
    - [_ProactorReadPipeTransport._loop_reading()]>
    -  self._write_fut = self._loop._proactor.send(self._sock, data)
4. Run and Write new Unit tests with different tunes

## Benchmark
#### Single threaded
1. Execution time for len = 100: 44.072s
#### Added: Asyncio via multiprocessor + concurrent connection, 10K parallel connections per proc [502 errors]
2. Execution time for len = 100: 8.0190 seconds
3. Execution time for len = 1000: 75.7620 seconds **[502 errors]**
#### Added: Asyncfiles, tuned concurrency to 50, buffer to 50K, procs to 8 [502 errors]
4. Execution time for len = 1000: 4.1863 seconds 
#### tuned concurrency to 5, per proc [PASSED NO ERROR]
5. Execution time for len = 1000: 82.6812 seconds, NO SERVER OVERWHELM 502 ERRORS. Anyway it is 31 hours, which is slow.
```
WARNING:scrap_process:Error 404: https://breadl.org/d/298 <--- THESE BOOKS INDEXES ARE ABSENT
WARNING:scrap_process:Error 404: https://breadl.org/d/300
WARNING:scrap_process:Error 404: https://breadl.org/d/53
WARNING:scrap_process:Error 404: https://breadl.org/d/366 <--->
```
#### tuned concurrency to 10, per proc [PASSED NO ERROR]
6. Execution time for len = 1000: 76.6256 seconds, 29.79 hours
```
WARNING:scrap_process:Error 404: https://breadl.org/d/298 
WARNING:scrap_process:Error 404: https://breadl.org/d/300
WARNING:scrap_process:Error 404: https://breadl.org/d/53
WARNING:scrap_process:Error 404: https://breadl.org/d/366
```

## Observations
When you get something like **below** cmd output, it means you overwhelmed server. Increase the timeout in scrap_process.py::scrape_page() to >10. Additionally, reduce parallel requests (concurrent sessions per process):
```python
semaphore = asyncio.Semaphore(5)  # Allow only 5 requests at a time per process (proc_num), I was getting 502 error at 500 parallel connections
...
async with retry_client.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as response:
```
CMD example output:
```
TimeoutError
ERROR:scrap_process:Exception fetching https://breadl.org/d/484:
TimeoutError
WARNING:scrap_process:Error 502: https://breadl.org/d/491
WARNING:scrap_process:Error 502: https://breadl.org/d/997
WARNING:scrap_process:Error 502: https://breadl.org/d/504
WARNING:scrap_process:Error 502: https://breadl.org/d/1005
WARNING:scrap_process:Error 502: https://breadl.org/d/616
WARNING:scrap_process:Error 502: https://breadl.org/d/1001
WARNING:scrap_process:Error 502: https://breadl.org/d/872
WARNING:scrap_process:Error 502: https://breadl.org/d/618
WARNING:scrap_process:Error 502: https://breadl.org/d/630
WARNING:scrap_process:Error 502: https://breadl.org/d/876
WARNING:scrap_process:Error 502: https://breadl.org/d/623
WARNING:scrap_process:Error 502: https://breadl.org/d/243
WARNING:scrap_process:Error 502: https://breadl.org/d/870
WARNING:scrap_process:Error 502: https://breadl.org/d/868
WARNING:scrap_process:Error 502: https://breadl.org/d/753
WARNING:scrap_process:Error 502: https://breadl.org/d/235
WARNING:scrap_process:Error 502: https://breadl.org/d/740
WARNING:scrap_process:Error 502: https://breadl.org/d/746
WARNING:scrap_process:Error 502: https://breadl.org/d/879
WARNING:scrap_process:Error 502: https://breadl.org/d/873
WARNING:scrap_process:Error 502: https://breadl.org/d/253
WARNING:scrap_process:Error 502: https://breadl.org/d/490
WARNING:scrap_process:Error 502: https://breadl.org/d/237
WARNING:scrap_process:Error 502: https://breadl.org/d/495
WARNING:scrap_process:Error 502: https://breadl.org/d/245
WARNING:scrap_process:Error 502: https://breadl.org/d/502
WARNING:scrap_process:Error 502: https://breadl.org/d/250
WARNING:scrap_process:Error 502: https://breadl.org/d/488
WARNING:scrap_process:Error 502: https://breadl.org/d/248
WARNING:scrap_process:Error 502: https://breadl.org/d/249
WARNING:scrap_process:Error 502: https://breadl.org/d/492
WARNING:scrap_process:Error 502: https://breadl.org/d/232
WARNING:scrap_process:Error 502: https://breadl.org/d/236
WARNING:scrap_process:Error 502: https://breadl.org/d/119
WARNING:scrap_process:Error 502: https://breadl.org/d/129
WARNING:scrap_process:Error 502: https://breadl.org/d/754
WARNING:scrap_process:Error 502: https://breadl.org/d/751
WARNING:scrap_process:Error 502: https://breadl.org/d/752
WARNING:scrap_process:Error 502: https://breadl.org/d/734
WARNING:scrap_process:Error 502: https://breadl.org/d/372
WARNING:scrap_process:Error 502: https://breadl.org/d/747
WARNING:scrap_process:Error 502: https://breadl.org/d/732
WARNING:scrap_process:Error 502: https://breadl.org/d/737
WARNING:scrap_process:Error 502: https://breadl.org/d/374
WARNING:scrap_process:Error 502: https://breadl.org/d/750
WARNING:scrap_process:Error 502: https://breadl.org/d/749
WARNING:scrap_process:Error 502: https://breadl.org/d/733
WARNING:scrap_process:Error 502: https://breadl.org/d/370
WARNING:scrap_process:Error 502: https://breadl.org/d/376
WARNING:scrap_process:Error 502: https://breadl.org/d/128
WARNING:scrap_process:Error 502: https://breadl.org/d/120
WARNING:scrap_process:Error 502: https://breadl.org/d/123
WARNING:scrap_process:Error 502: https://breadl.org/d/130
ERROR:scrap_process:Exception fetching https://breadl.org/d/736:
Traceback (most recent call last):
    message, payload = await protocol.read()  # type: ignore[union-attr]
The above exception was the direct cause of the following exception:

Traceback (most recent call last):
    async with retry_client.get(url, timeout=4, headers={"User-Agent": "Mozilla/5.0"}) as response:#to avoid ban, hopefully
               ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    return await self._do_request()
           ^^^^^^^^^^^^^^^^^^^^^^^^
    response: ClientResponse = await self._request_func(
                               ^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<8 lines>...
    )
    ^
    with self._timer:
         ^^^^^^^^^^^
    raise asyncio.TimeoutError from exc_val
TimeoutError
ERROR:scrap_process:Exception fetching https://breadl.org/d/755:
Traceback (most recent call last):
    message, payload = await protocol.read()  # type: ignore[union-attr]
                       ^^^^^^^^^^^^^^^^^^^^^
    await self._waiter
asyncio.exceptions.CancelledError
```