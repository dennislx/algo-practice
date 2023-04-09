import multiprocessing as mp
import sys

from mkdocs_writer import MkdocsWriter

if __name__ == "__main__":
  leetcode_api = MkdocsWriter(sys.argv)
  manager = mp.Manager()
  finished_problems, lock = manager.dict(), manager.Lock()
  pool = mp.Pool(processes=1)
  pool.apply_async(leetcode_api.write_problems, (finished_problems, lock, ))
  pool.close()# no more tasks will be submitted to run
  pool.join() # wait for the pool to finish before continue
  leetcode_api.write_mkdocs(finished_problems)
