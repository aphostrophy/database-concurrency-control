from typing import Callable, List
from ..database import Database

Transaction = Callable[[Database], None]