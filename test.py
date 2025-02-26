import unittest
import time
from app import launch as foo

class TestFetchData(unittest.TestCase):

    def test_fetch_data_execution_time(self):
        start_id = 6
        end_id = 1403112
        proc_num = 8
        concurrency = 50
        buffer_size = 10000 * 5
        out_file = "E:/libgen_books_and_mirrors.txt"

        test_lens = [
            1000,
            #end_id - start_id
        ]
        #Execution time for len = 100: 44.072s single threaded via requests
        #Execution time for len = 100: 8.0190 seconds asyncio via multiprocessor + concurrent connection
        #Execution time for len = 1000: 75.7620 seconds
        #Execution time for len = 1000: 4.1863 seconds introduced asyncfiles, tuned concurrency, buffer, procs
        
        for len in test_lens:
            start_time = time.time()
            foo(proc_num, concurrency, buffer_size, out_file, start_id, start_id + len)
            end_time = time.time()
            execution_time = end_time - start_time  # Measure execution time
            print(f"Execution time for len = {len}: {execution_time:.4f} seconds")
            
            #self.assertIsInstance(result, tuple)  # Ensure the function returns a string
            #self.assertLess(execution_time, 2, f"Fetch took too long: {execution_time:.4f}s")

if __name__ == "__main__":
    unittest.main()