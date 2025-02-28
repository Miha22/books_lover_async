import unittest
from datetime import datetime
import os
from app import launch as foo

class TestFetchData(unittest.TestCase):
    def test_fetch_data_execution_time(self):
        start_id = 6
        end_id = 1403112
        proc_num = 4
        concurrency = 20
        buffer_size = 10000 * 5

        test_lens = [
            500
        ]
        offset = 0
        start_id = 6 + offset
        
        for len in test_lens:
            end_id = start_id + len - 1
            
            out_file = f"out/books_{start_id}_{end_id}_{proc_num}_{concurrency}_{len}.txt"
            r = foo(proc_num, concurrency, buffer_size, out_file, start_id, end_id, 3)

            file_size = os.stat(out_file).st_size
            with open("benchmark.txt", "a") as f:
                f.write(f"Processes: {proc_num}\nConcurrency: {concurrency}\nBooks fetched: {len} ({start_id}-{end_id})\nBooks Missed: {r[0]}/{len} timeouts\nLoss: {r[1]:.2f}%\nExecution time for len = {len}: {r[2]:.2f} seconds\nSpeed: {r[3]:.2f} books/sec\nFile size: {file_size / 1000000.0} MB\nTimestamp: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n")
            
            print(f"Total Timeouts: {r[0]}/{len} books")
            print(f"Loss: {r[1]:.2f}%")
            print(f"Execution time for len = {len}: {r[2]:.2f} seconds")
            print(f"Speed: {r[3]:.2f} books/sec")
            print(f"File size: {file_size / 1000000.0} MB")
            #self.assertIsInstance(result, tuple)  # Ensure the function returns a string
            #self.assertLess(execution_time, 2, f"Fetch took too long: {execution_time:.4f}s")

if __name__ == "__main__":
    unittest.main()