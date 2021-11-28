from typing import List, Any
from occ.database import DatabaseCacheExecutorWrapper
from occ.txn_processor import SerialDatabase, TxnProcessor
from occ.typings.transaction import Transaction
from time import sleep

def main():
  def init() -> Transaction:
    def txn(db:DatabaseCacheExecutorWrapper) -> None:
      db.write('x', 0)
      db.write('y', 0)
      db.write('z', 0)
    return txn

  def transactionOne(x= 'x', y= 'y', z= 'z') -> Transaction:
    def txn(db: DatabaseCacheExecutorWrapper) -> None:
      x_val = db.read(x)
      db.write(x, x_val+1)
    return txn

  def transactionOneA(x= 'x', y= 'y', z= 'z') -> Transaction:
    def txn(db: DatabaseCacheExecutorWrapper) -> None:
      z_val = db.read(z)
      db.write(z, z_val+1)
    return txn

  def transactionTwo(x= 'x', y= 'y', z= 'z') -> Transaction:
    def txn(db: DatabaseCacheExecutorWrapper) -> None:
      x_val = db.read(x)
      y_val = db.read(y)
      db.write(x, x_val+1)
      db.write(y, y_val+3)
    return txn

  def transactionThree(x= 'x', y= 'y', z= 'z') -> Transaction:
    def txn(db: DatabaseCacheExecutorWrapper) -> None:
      x_val = db.read(x)
      y_val = db.read(y)
      z_val = db.read(z)
      db.write(x, x_val+1)
      db.write(y, y_val+1)
      db.write(z, z_val+1)
    return txn

  init_db = init()

  db = SerialDatabase()
  assert(db.data == {})

  processor = TxnProcessor(db)

  processor.enqueue_transaction(init_db)
  processor.execute()

  ''' END OF INIT DB'''

  t_1 = transactionOne()
  t_1_A = transactionOneA()
  t_2 = transactionTwo()

  processor.enqueue_transaction(t_1)
  processor.enqueue_transaction(t_2)
  processor.enqueue_transaction(t_1_A)

  processor.execute()
  print(db.data)

  t_3 = transactionThree()
  processor.enqueue_transaction(t_3)
  processor.execute()
  print(db.data)

if __name__ == '__main__':
  main()