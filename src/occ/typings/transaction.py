from typing import Callable
from ..database import DatabaseCacheExecutorWrapper

Transaction = Callable[[DatabaseCacheExecutorWrapper], None]