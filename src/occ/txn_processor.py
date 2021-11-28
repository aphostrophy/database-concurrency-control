from typing import Any, Dict
from occ.typings.transaction import Transaction

from occ.database import Database, DatabaseCacheExecutorWrapper

class SerialTransactionExecutor:
  def __init__(self, db: 'SerialDatabase' , txn: Transaction) -> None:
    self.db = db
    self.cached_db = DatabaseCacheExecutorWrapper(db)
    self.txn = txn
    self.start_ts = self.db._get_tsc()

  def read_phase(self) -> None:
    self.txn(self.cached_db)

  def validate_and_write_phase(self) -> bool:
    finish_ts = self.db._get_tsc()
    '''
      Check for every Tj s.t. startTS(Tj) < finishTS(Ti) < endTS(Tj) , write set of j doesn't intersect with read set of self (i)
    '''
    read_set_i = self.cached_db.get_read_set()
    for ts in range(self.start_ts + 1, finish_ts + 1):
      cached_db = self.db._get_transaction(ts)
      write_set_j = cached_db.get_write_set()
      if not write_set_j.isdisjoint(read_set_i):
        return False

    self.db._commit_transaction(self.cached_db)
    return True


class SerialDatabase(Database):
  '''
    Database with timestamp tracker
  '''
  def __init__(self):
    Database.__init__(self)
    self.transactions: Dict[int, DatabaseCacheExecutorWrapper] = {}
    self.tsc: int = 0

  def _get_tsc(self):
    return self.tsc

  def _get_transaction(self, tn:int) -> DatabaseCacheExecutorWrapper:
    assert tn in self.transactions
    return self.transactions[tn]

  def _commit_transaction(self,db: DatabaseCacheExecutorWrapper) -> None:
    self.tsc += 1
    assert self.tsc not in self.transactions
    self.transactions[self.tsc] = db
    db.commit()

  def begin(self, txn: Transaction) -> SerialTransactionExecutor:
    return SerialTransactionExecutor(self, txn)