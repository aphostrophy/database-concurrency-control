from typing import Any, Dict
import threading

class Database:
  """
  Persistent Database
  """
  def __init__(self) -> None:
    self.data : Dict[str, Any] = {}

  def write(self, key: str, val: Any) -> None:
    self.data[key] = val

  def read(self, key: str) -> Any:
    assert key in self.data
    return self.data[key]

  def delete(self, key: str) -> None:
    del self.data[key]
