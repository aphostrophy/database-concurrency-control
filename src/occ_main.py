from typing import List
from occ.database import DatabaseCacheExecutorWrapper
from occ.txn_processor import SerialDatabase
from occ.typings.transaction import Transaction

def main():
  print('This is OCC main driver')

if __name__ == '__main__':
  def init(db: DatabaseCacheExecutorWrapper) -> None:
    db.write('x', 0)
    db.write('y', 0)
    db.write('z', 0)

  def incr_vars(vs: List[str]) -> Transaction:
    def txn(db: DatabaseCacheExecutorWrapper) -> None:
      for v in vs:
        x = db.read(v)
        db.write(v, x + 1)
    return txn

  incr_x = incr_vars(['x'])
  incr_y = incr_vars(['y'])
  incr_z = incr_vars(['z'])
  incr_all = incr_vars(['x', 'y', 'z'])

  db = SerialDatabase()
  assert(db.data == {})

  t_init = db.begin(init)
  t_init.read_phase()
  assert(t_init.validate_and_write_phase())
  assert(db.data == {'x': 0, 'y': 0, 'z': 0})

  # t_1 and t_2 run concurrently and have conflicting read and write sets, so
  # whichever transaction attempts to commit first (i.e. t_1) succeeds. The
  # other (i.e. t_2) fails and is forced to abort.
  t_1 = db.begin(incr_all)
  t_2 = db.begin(incr_all)
  t_1.read_phase()
  t_2.read_phase()
  assert(t_1.validate_and_write_phase())
  assert(not t_2.validate_and_write_phase())
  assert(db.data == {'x': 1, 'y': 1, 'z': 1})

  # t_3 and t_4 run concurrently, but have disjoint read and write sets, so
  # they can both commit.
  t_3 = db.begin(incr_x)
  t_4 = db.begin(incr_y)
  t_3.read_phase()
  t_4.read_phase()
  assert(t_3.validate_and_write_phase())
  assert(t_4.validate_and_write_phase())
  assert(db.data == {'x': 2, 'y': 2, 'z': 1})