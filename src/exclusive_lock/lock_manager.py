from typing import List, Dict
from time import sleep
from multiprocessing.connection import Connection
from exclusive_lock.messages import ACQUIRE, RELEASE, TERMINATE
from utils.mutex import Mutex

class LockManager():
  """
  Lock manager implementation using lock table
  """
  def __init__(self, resources: List[str], conn: Connection) -> None:
    self.lock_table: Dict[str, List] = {key: [] for key in resources}
    self.conn = conn
    self.running = True

  def _acquire_lock(self, resource_name: str, transaction_number: int) -> None:
    assert transaction_number not in self.lock_table[resource_name]
    if(len(self.lock_table[resource_name]) == 0):
      print(f'Transaction {transaction_number} XL {resource_name}')
      response = {"message" : ACQUIRE, "transaction_number": transaction_number, "resource_name": resource_name}
      self.conn.send(response)
    self.lock_table[resource_name].append(transaction_number)
  
  def _release_lock(self, resource_name: str, transaction_number: int) -> None:
    assert(self.lock_table[resource_name][0]==transaction_number)
    self.lock_table[resource_name].pop()
    print(f'Transaction {transaction_number} UL {resource_name}')
    if(len(self.lock_table[resource_name]) > 0):
      next_transaction_number = self.lock_table[resource_name]
      print(f'Transaction {next_transaction_number} XL {resource_name}')
      response = {"message" : ACQUIRE, "transaction_number" : next_transaction_number, "resource_name": resource_name}
      self.conn.send(response)

  def start(self) -> None:
    self.running = True
    while(self.running):
      sleep(0.1)
      request = self.conn.recv()

      if(request['message'] == TERMINATE):
        print("END LOCK MANAGER")
        print("===============")
        self.running = False
        self.conn.send({"message": TERMINATE})
        self.conn.close()
      elif(request['message'] == ACQUIRE):
        assert 'resource_name' in request
        assert 'transaction_number' in request
        self._acquire_lock(request['resource_name'], request['transaction_number'])
      elif(request['message'] == RELEASE):
        assert 'resource_name' in request
        assert 'transaction_number' in request
        self._release_lock(request['resource_name'], request['transaction_number'])