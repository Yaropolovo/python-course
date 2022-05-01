"""Module for Inverted Index"""
from __future__ import annotations

from typing import Dict, List
import re
import json

class InvertedIndex:
    """Class for realization of Inverted Index (and relevant methods)"""
    def __init__(self, index_as_dict: Dict[str, list]):
        """Initialization by data as a dict"""
        self.data = index_as_dict

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        if len(words) == 0:
            found_documents = []
        else:
            found_documents = self.data.get(words[0], [])
            for word in words[1:]:
                list_for_word = self.data.get(word, [])
                found_documents = list(set(found_documents) & set(list_for_word))
        return found_documents

    def dump(self, filepath: str) -> None:
        """Save data into json"""
        with open(filepath, 'w') as fout:
            json.dump(self.data, fout)

    @classmethod
    def load(cls, filepath: str) -> InvertedIndex:
        """Load data from json"""
        with open(filepath, 'r') as fin:
            loaded_dict = json.load(fin)
        return InvertedIndex(loaded_dict)

    def __eq__(self, rhs):
        """Compare objects by stored data"""
        outcome = (
            self.data == rhs.data
        )
        return outcome

def load_documents(filepath: str) -> Dict[int, str]:
    """Read documnets from .txt file"""
    loaded_dict = {}
    with open(filepath) as fin:
        text = fin.read().strip().split('\n')
        for line in text:
            document_index, document_text = line.lower().split('\t', 1)
            loaded_dict[int(document_index)] = document_text #re.split(r"\W+", document_text)
    return loaded_dict

def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """Build InvertedIndex object from list of documents"""
    index_as_dict = {}
    for document_index in documents.keys():
        words = list(set(re.split(r"\W+", documents[document_index])))
        for word in words:
            if index_as_dict.get(word) is None:
                index_as_dict[word] = [document_index]
            else:
                index_as_dict[word] = index_as_dict[word] + [document_index]
    return InvertedIndex(index_as_dict)


def main():
    """Main function"""
    documents = load_documents("/path/to/dataset")
    inverted_index = build_inverted_index(documents)
    inverted_index.dump("/path/to/inverted.index")
    inverted_index = InvertedIndex.load("/path/to/inverted.index")
    document_ids = inverted_index.query(["two", "words"])


if __name__ == "__main__":
    main()
