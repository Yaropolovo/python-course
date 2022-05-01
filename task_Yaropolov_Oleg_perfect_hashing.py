from typing import List
import array
import struct
from random import randrange

# https://docs.python.org/2/library/sys.html#sys.maxint
LONG_SIZE_IN_BYTES = struct.calcsize('l')
MIN_INT = -2 ** (8 * LONG_SIZE_IN_BYTES - 1)
MAX_TRIALS = 4
HUGE_PRIME_NUMBER = 2147483647

class HashTableChain:
    """classical hash table implementation (for comparison with perfect hash)"""
    __slots__ = ("hash_function", "collection_size", "counts", "hash_table")

    def __init__(self, collection: List[int], hash_function=None):
        """Generate HashTable for collection"""
        self.hash_function = hash_function or hash
        self.collection_size = len(collection)
        self.fill_hash_table(collection)

    def fill_hash_table(self, collection: List[int]):
        """Adding all elements to HashTable with chain solution for collision"""
        self.counts = array.array("l", [0] * self.collection_size)
        self.hash_table = [[]] * self.collection_size
        for element in collection:
            key = self.hash_function(element) % self.collection_size
            if self.counts[key] > 0:
                self.hash_table[key].append(element)
            else:
                self.hash_table[key] = array.array("l", [element])
            self.counts[key] += 1

    def __contains__(self, item) -> bool:
        """checking by key, then checking the whole chain if exists"""
        key = self.hash_function(item) % self.collection_size
        if self.counts[key] == 0:
            return False
        else:
            output = any(item == element for element in self.hash_table[key])
            return output


class HashTablePerfect:
    """build static hash table with < 4n memory space with universal hash family"""
    __slots__ = ("hash_first_level", "hash_second_level", "collection_size", "counts", "hash_table")

    def __init__(self, collection: List[int], max_trials=MAX_TRIALS):
        """Generate HashTable for collection"""
        self.collection_size = len(collection)
        self.fill_hash_table(collection)

    def get_random_hash_function(self):
        a, b = randrange(1, HUGE_PRIME_NUMBER), randrange(0, HUGE_PRIME_NUMBER)
        def hash_function(input: int, m: int) -> int:
            output = ((a * input + b) % HUGE_PRIME_NUMBER) % m
            return output
        return hash_function

    def fill_hash_table(self, collection: List[int]):
        """
        Building two-level perfect hash

        * For second-level tables we are able to use HashTableChain class,
        but for efficiency let's reimplement it
        * For second iteration of hashing we could store or recalculate
        bucket_numbers from first iteation depending on time or memory
        optimization. I've chosen to recalculate
        """
        is_not_builded_successfully = True
        current_trial = 0
        while is_not_builded_successfully:
            current_trial += 1
            if current_trial > MAX_TRIALS:
                raise ValueError("cannot build perfect hash table within %s trials" % MAX_TRIALS)

            self.counts = array.array("l", [0] * self.collection_size)
            self.hash_table = [array.array("l", [])] * self.collection_size

            # pick random hash functions:
            self.hash_first_level = self.get_random_hash_function()
            self.hash_second_level = self.get_random_hash_function()

            # hashing. First iteration
            for element in collection:
                key = self.hash_first_level(element, self.collection_size)
                self.counts[key] += 1

            sum_of_squares = sum(bucket_size ** 2 for bucket_size in self.counts)
            starting_over = sum_of_squares > 4 * self.collection_size
            if starting_over:
                continue

            # hashing. Second iteration
            collision_detected = False
            for element in collection:
                bucket_number = self.hash_first_level(element, self.collection_size)
                key = self.hash_second_level(element, self.counts[bucket_number] ** 2)
                if self.hash_table[bucket_number] == array.array("l", []):
                    # Is not initialized before
                    self.hash_table[bucket_number] = array.array("l", [MIN_INT] * self.counts[bucket_number] ** 2)
                elif self.hash_table[bucket_number][key] != MIN_INT:
                    # print("collision!")
                    collision_detected = True
                    break
                self.hash_table[bucket_number][key] = element

            if collision_detected:
                continue

            # success, if we are here!
            is_not_builded_successfully = False

    def __contains__(self, item) -> bool:
        bucket_number = self.hash_first_level(item, self.collection_size)
        if self.hash_table[bucket_number] == array.array("l", []):
            return False
        else:
            key = self.hash_second_level(item, self.counts[bucket_number] ** 2)
            item_is_presented = (self.hash_table[bucket_number][key] == item)
            return item_is_presented
