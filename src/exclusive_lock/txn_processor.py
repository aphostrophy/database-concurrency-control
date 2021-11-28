from multiprocessing.connection import Connection
from threading import get_ident
from typing import List
from time import sleep
from exclusive_lock.database import Database
from exclusive_lock.messages import ACQUIRE
from exclusive_lock.typings.transaction import Transaction

class TxnProcessor():
  def __init__(self, conn: Connection, db : Database):
    self.conn = conn
    self.db = db
    self.txnQueue : List = []
    self.pendingTxn: List = []

  def enqueue_transaction(self,txn : Transaction):
    self.txnQueue.append(txn)

  def start(self):
    running = True
    while(running):
      sleep(2)
      request = {}
      request['message'] = ACQUIRE
      request['transaction_number'] = get_ident()
      request['resource_name'] = 'x'
      self.conn.send(request)
      response = self.conn.recv()
      print(response)

class TransactionExecutor():
  def __init__(self, conn: Connection, db: Database):
    self.conn = conn
    self.db = db
    self.transaction_number = get_ident()