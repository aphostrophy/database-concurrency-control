from typing import Dict, List
from threading import Thread, get_ident

from occ.typings.transaction import Transaction, Operation
from occ.database import Database, DatabaseCacheExecutorWrapper
from utils.mutex import Mutex

class TxnProcessor:
  def __init__(self, db: 'SerialDatabase') -> None:
    self.db = db
    self.txnQueue : List = []
    self.pendingTxn: List = []

  def enqueue_transaction(self, txn: Transaction) -> None:
    self.txnQueue.append(txn)
  
  def execute(self) -> None: 
    while(len(self.txnQueue)!=0):
      tn = self.txnQueue.pop()
      tn_executor = self.db.get_executor(tn)
      t = Thread(target=tn_executor.execute_concurrent, args=())
      self.pendingTxn.append(t)
      t.start()
    
    for t in self.pendingTxn:
      t.join()

  def restart(self):
    self.txnQueue = []
    self.pendingTxn = []
    print('TxnProcessor Refreshed')

class SerialTransactionExecutor:
  def __init__(self, db: 'SerialDatabase' , txn: Transaction) -> None:
    self.db = db
    self.cached_db = DatabaseCacheExecutorWrapper(db)
    self.txn = txn
    self.start_ts = self.db._get_tsc()

  def execute_concurrent(self) -> None:
    self._read_and_execution_phase()
    self._validate_and_write_phase()

  def _read_and_execution_phase(self) -> None:
    self.txn(self.cached_db)

  def _validate_and_write_phase(self) -> bool:
    finish_ts = self.db._get_tsc()
    '''
      Check for every Tj s.t. startTS(Tj) < finishTS(Ti) < endTS(Tj) , write set of j doesn't intersect with read set of self (i)
    '''
    read_set_i = self.cached_db.get_read_set()
    for ts in range(self.start_ts + 1, finish_ts + 1):
      cached_db = self.db._get_transaction(ts)
      write_set_j = cached_db.get_write_set()
      if not write_set_j.isdisjoint(read_set_i):
        print(f'Thread {get_ident()} is ROLLED BACK')
        return False

    self.db._commit_transaction(self.cached_db)
    print(f'Thread {get_ident()} is COMMITING')
    return True


class SerialDatabase(Database):
  '''
    Database with timestamp tracker
  '''
  def __init__(self) -> None:
    Database.__init__(self)
    self.transactions: Dict[int, DatabaseCacheExecutorWrapper] = {}
    self.tsc: int = 0

  def _get_tsc(self):
    return self.tsc

  def _get_transaction(self, tn:int) -> DatabaseCacheExecutorWrapper:
    assert tn in self.transactions
    return self.transactions[tn]

  def _increment_tsc(self) -> None:
    Mutex.acquire()
    self.tsc += 1
    Mutex.release()

  def _commit_transaction(self,db: DatabaseCacheExecutorWrapper) -> None:
    Mutex.acquire()

    self.tsc += 1
    assert self.tsc not in self.transactions
    self.transactions[self.tsc] = db
    db.commit()
    
    Mutex.release()

  def get_executor(self, txn: Transaction) -> SerialTransactionExecutor:
    return SerialTransactionExecutor(self, txn)