from typing import Callable, List
from ..database import DatabaseCacheExecutorWrapper

Operation = Callable[[DatabaseCacheExecutorWrapper], None]

Transaction = List[Operation]