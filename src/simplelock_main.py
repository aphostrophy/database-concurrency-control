from multiprocessing import Lock, Pipe
import multiprocessing
from exclusive_lock.lock_manager import LockManager
from exclusive_lock.txn_processor import TransactionExecutor, TxnProcessor, Transaction
from exclusive_lock.database import Database
from time import sleep

def main():
  def init() -> Transaction:
    def txn(tn:TransactionExecutor) -> None:
      tn.write('x', 0)
      tn.write('y', 0)
      tn.write('z', 0)
    return txn

  def transactionOne(x= 'x', y= 'y', z= 'z') -> Transaction:
    def txn(tn:TransactionExecutor) -> None:
      x_val = tn.read(x)
      tn.write(x, x_val+1)
    return txn

  def transactionTwo(x= 'x', y= 'y', z= 'z') -> Transaction:
    def txn(tn:TransactionExecutor) -> None:
      y_val = tn.read(y)
      tn.write(y, y_val+1)
    return txn

  def transactionThree(x= 'x', y= 'y', z= 'z') -> Transaction:
    def txn(tn:TransactionExecutor) -> None:
        x_val = tn.read(x)
        y_val = tn.read(y)
        tn.write(x, x_val+1)
        tn.write(y, y_val+3)
    return txn

  def transactionFour(x= 'x', y= 'y', z='z') -> Transaction:
    def txn(tn:TransactionExecutor) -> None:
      z_val = tn.read(z)
      y_val = tn.read(y)
      tn.write(y, y_val + z_val)
      x_val = tn.read(x)
      tn.write(x, x_val + y_val + z_val)
    return txn

  resources = ['x','y','z']

  db = Database()
  init_db = init()

  lock_manager_conn, txn_processor_conn = Pipe()
  
  lock_manager = LockManager(resources, lock_manager_conn)
  txn_processor = TxnProcessor(txn_processor_conn, db)

  lock_manager_process = multiprocessing.Process(target=lock_manager.start, args=())
  lock_manager_process.start()

  txn_processor.enqueue_transaction(init_db)
  txn_processor.start()

  sleep(1)

  lock_manager_process = multiprocessing.Process(target=lock_manager.start, args=())
  lock_manager_process.start()

  t_1 = transactionOne()
  t_2= transactionTwo()
  t_3 = transactionThree()
  t_4 = transactionFour()

  txn_processor.enqueue_transaction(t_1)
  txn_processor.enqueue_transaction(t_2)
  txn_processor.enqueue_transaction(t_3)
  # txn_processor.enqueue_transaction(t_4)
  txn_processor.start()

if __name__ == '__main__':
  main()