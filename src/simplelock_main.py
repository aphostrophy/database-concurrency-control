from multiprocessing import Lock, Pipe
import multiprocessing
from exclusive_lock.lock_manager import LockManager
from exclusive_lock.txn_processor import TxnProcessor
from exclusive_lock.database import Database

def main():
  resources = ['x','y','z']

  db = Database()

  lock_manager_conn, txn_processor_conn = Pipe()
  
  lock_manager = LockManager(resources, lock_manager_conn)
  txn_processor = TxnProcessor(txn_processor_conn, db)

  lock_manager_process = multiprocessing.Process(target=lock_manager.start, args=())
  lock_manager_process.start()

  txn_processor.start()

if __name__ == '__main__':
  main()