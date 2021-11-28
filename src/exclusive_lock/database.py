from typing import Any, Dict, Set
import threading

class Database:
  """
  Persistent Database
  """
  def __init__(self) -> None:
    self.data : Dict[str, Any] = {}

  def write(self, key: str, val: Any) -> None:
    print(f'Thread {threading.get_ident()} is WRITING {key}:{val} to database')
    self.data[key] = val

  def read(self, key: str) -> Any:
    assert key in self.data
    print(f'Thread {threading.get_ident()} is READING {key}:{self.data[key]} from database')
    return self.data[key]

  def delete(self, key: str) -> None:
    del self.data[key]