from typing import Any, Dict, Set, Callable

class Database:
  """
  Persistent Database
  """
  def __init__(self) -> None:
    pass


class CacheDatabase:
  """
  Cache Memory Database
  """
  def __init__(self) -> None:
    pass



class DatabaseCacheExecutorWrapper:
  """
  Wrapper to handle write/read/delete operation. This class contains the persistent database (Database Object)
  and the in memory database (Cache Database Object) to buffer the operations before commit. If the optimistic
  concurrency control validation passes, it will commit and write from the Cache Database into the Database
  Object permanently
  """
  def __init__(self) -> None:
    pass