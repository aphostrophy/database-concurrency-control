from multiprocessing.connection import Connection
from threading import Thread, get_ident
from typing import List, Any, Callable, Dict
from time import sleep, time
from exclusive_lock.database import Database
from exclusive_lock.messages import ACQUIRE, RELEASE, TERMINATE, ABORT
from utils.mutex import Mutex

TIME_LIMIT = 3

class TxnProcessor():
  def __init__(self, conn: Connection, db : Database):
    self.conn = conn
    self.db = db
    self.txnQueue : List = []
    self.pendingTxn: List = []
    self.messageQueue: Dict[str, List] = {}

    self.t_num = 0

  def enqueue_transaction(self,txn : 'Transaction'):
    self.txnQueue.append(txn)

  def start(self):
    self.isListening = True
    listener = Thread(target=self.listener, args=())
    listener.start()
    while(len(self.txnQueue)!=0):
      tn = self.txnQueue.pop(0)
      tn_executor = TransactionExecutor(self.conn, self.db, tn, self.messageQueue, self.t_num)
      self.t_num += 1
      t = Thread(target=tn_executor.execute_concurrent, args=())
      self.pendingTxn.append(t)
      t.start()
    
    for t in self.pendingTxn:
      t.join()

    self.clear()

  def listener(self):
    while(self.isListening):
      try:
        response = self.conn.recv()
        if(response['message'] == TERMINATE):
          self.isListening = False
          break
        assert 'transaction_number' in response
        messageQueueKey = response['transaction_number']
        self.messageQueue[messageQueueKey].append(response)
      except BrokenPipeError:
        print('Listener connection to lock manager has been closed')


  def clear(self):
    self.txnQueue = []
    self.pendingTxn = []
    self.conn.send({"message": TERMINATE})

class TransactionExecutor():
  def __init__(self, conn: Connection, db: Database, txn: 'Transaction', messageQueue: Dict[str, list], t_num: int):
    self.conn: Connection = conn
    self.db: Database = db
    self.txn: Transaction = txn
    self.messageQueue: Dict[str, list] = messageQueue
    self.locks: List = []
    self.transaction_number = t_num

  def execute_concurrent(self):
    self.messageQueue[self.transaction_number] = []
    try:
      self.txn(self)
      self.commit()
    except AssertionError:
      request = {"message": ABORT, "transaction_number": self.transaction_number}
      self.conn.send(request)
      print(f'{self.transaction_number} is aborted')

  def write(self, key: str, val: Any) -> None:
    if(key in self.locks):
      print(f'Transaction {self.transaction_number} WRITE {key}')
      self.db.write(key, val)
    else:
      request = {"message": ACQUIRE, "transaction_number": self.transaction_number, "resource_name": key}
      self.conn.send(request)
      timeCheck = time()
      try:
        while(True):
          sleep(0.05)
          if(time() > timeCheck + TIME_LIMIT):
            assert False
          for message in self.messageQueue[self.transaction_number]:
            assert 'message' in message
            if(message['message'] == ACQUIRE):
              assert 'resource_name' in message
              self.locks.append(message['resource_name'])
              self.messageQueue[self.transaction_number].pop(0)
              self.write(message['resource_name'],val)
              return None
      except AssertionError:
        self.abort()

  def read(self, key: str) -> Any:
    if(key in self.locks):
      print(f'Transaction {self.transaction_number} READ {key}')
      return self.db.read(key)
    else:
      request = {"message": ACQUIRE, "transaction_number": self.transaction_number, "resource_name": key}
      self.conn.send(request)
      timeCheck = time()
      try:
        while(True):
          sleep(0.05)
          if(time() > timeCheck + TIME_LIMIT):
            assert False
          for message in self.messageQueue[self.transaction_number]:
            assert 'message' in message
            if(message['message'] == ACQUIRE):
              assert 'resource_name' in message
              self.locks.append(message['resource_name'])
              self.messageQueue[self.transaction_number].pop(0)
              return self.read(message['resource_name'])
      except AssertionError:
        self.abort()

  def abort(self) -> None:
    print(f'Detected possible deadlock for transaction {self.transaction_number}')
    assert False
  
  def commit(self) -> None:
    print(f'Transaction {self.transaction_number} commit')
    while(len(self.locks)>0):
      resource_name = self.locks.pop(0)
      request = {"message": RELEASE, "transaction_number": self.transaction_number, "resource_name": resource_name}
      self.conn.send(request)

Transaction = Callable[[TransactionExecutor], None]