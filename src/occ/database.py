from typing import Any, Dict, Set
import threading

class Database:
  """
  Persistent Database
  """
  def __init__(self) -> None:
    self.data : Dict[str, Any] = {}

  def write(self, key: str, val: Any) -> None:
    print(f'Thread {threading.get_ident()} WRITE {key}')
    self.data[key] = val

  def read(self, key: str) -> Any:
    assert key in self.data
    print(f'Thread {threading.get_ident()} READ {key}')
    return self.data[key]

  def delete(self, key: str) -> None:
    del self.data[key]

class CacheDatabase:
  """
  Cache Memory Database to track writen values before commit, after DatabaseCacheExecutor commits, it 
  will map all the values inside CacheDatabase into the persistent database
  """
  def __init__(self) -> None:
    self.data : Dict[str, Any] = {}

  def _read(self, key: str) -> Any:
    assert key in self.data
    print(f'Thread {threading.get_ident()} READ {key} CACHE')
    return self.data[key]

  def _write(self, key: str, val: Any) -> None:
    print(f'Thread {threading.get_ident()} WRITE {key} CACHE')
    self.data[key] = val

  def _data(self) -> Dict[str, Any]:
    return self.data


class DatabaseCacheExecutorWrapper:
  """
  Wrapper to handle write/read/delete operation. This class contains the persistent database (Database Object)
  and the in memory database (Cache Database Object) to buffer the operations before commit. If the optimistic
  concurrency control validation passes, it will commit and write from the Cache Database into the Database
  Object permanently
  """
  def __init__(self, db: Database) -> None:
    self.db = db
    self.cache = CacheDatabase()
    self.read_set: Set[str] = set()

  def write(self, key: str, val: Any) -> None:
    self.cache._write(key,val)

  def read(self, key: str) -> Any:
    self.read_set.add(key)
    try:
      return self.cache._read(key)
    except AssertionError:
      return self.db.read(key)

  def commit(self) -> None:
    for key, value in self.cache._data().items():
      self.db.write(key, value)

  def get_write_set(self) -> Set[str]:
    return set(self.cache._data().keys())

  def get_read_set(self) -> Set[str]:
    return self.read_set