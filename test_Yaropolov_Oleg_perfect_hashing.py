import pytest
from timeit import timeit

from task_Yaropolov_Oleg_perfect_hashing import HashTablePerfect, HashTableChain

COLLECTION_PATH = "bad_input.txt"

@pytest.fixture
def data_for_testing():
    with open(COLLECTION_PATH) as fin:
        fast_key = int(fin.readline()[:-1])
        slow_key = int(fin.readline()[:-1])
        collection = list(map(int, fin.readline().strip().split(' ')))
    return fast_key, slow_key, collection

def test_perfect_hash_is_stable(data_for_testing):
    fast_key, slow_key = data_for_testing[0], data_for_testing[1]
    collection = data_for_testing[2]

    hash_table = HashTablePerfect(collection)
    fast_time = timeit(lambda: fast_key in hash_table)
    slow_time = timeit(lambda: slow_key in hash_table)
    assert slow_time / fast_time <= 5

def test_chain_hash_is_not_stable(data_for_testing):
    fast_key, slow_key = data_for_testing[0], data_for_testing[1]
    collection = data_for_testing[2]

    hash_table = HashTableChain(collection, hash_function=hash)
    fast_time = timeit(lambda: fast_key in hash_table)
    slow_time = timeit(lambda: slow_key in hash_table)
    assert slow_time / fast_time >= 30
    