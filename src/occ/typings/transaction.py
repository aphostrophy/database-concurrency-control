from typing import Callable, List
from ..database import DatabaseCacheExecutorWrapper

Transaction = Callable[[DatabaseCacheExecutorWrapper], None]