from pytest import raises
from .dbf import DBF
from .exceptions import MissingMemoFile

def test_missing_memofile():
    with raises(MissingMemoFile):
        DBF('testcases/no_memofile.dbf')

    # This should succeed.
    table = DBF('testcases/no_memofile.dbf', ignore_missing_memofile=True)

    # Memo fields should be returned as None.
    record = next(iter(table))
    assert record['MEMO'] is None
