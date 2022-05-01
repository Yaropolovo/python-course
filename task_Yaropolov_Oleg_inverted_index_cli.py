"""Module for Inverted Index"""
from __future__ import annotations
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import Dict, List
import sys
import re
import json

DEFAULT_DATASET_PATH = "./wikipedia_sample"
DEFAULT_OUTPUT_PATH = "./inverted_index"
DEFAULT_STORAGE_POLICY = "json"

class InvertedIndex:
    """Class for realization of Inverted Index (and relevant methods)"""
    def __init__(self, index_as_dict: Dict[str, list]):
        """Initialization by data as a dict"""
        self.data = index_as_dict

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        assert isinstance(words, list)
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
        print(f"Dumping inverted index into {filepath}...", file=sys.stderr)
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
    print(f"Loading documents from {filepath}...", file=sys.stderr)
    loaded_dict = {}
    with open(filepath, encoding='utf-8') as fin:
        text = fin.read().strip().split('\n')
        for line in text:
            document_index, document_text = line.lower().split('\t', 1)
            loaded_dict[int(document_index)] = document_text #re.split(r"\W+", document_text)
    return loaded_dict

def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """Build InvertedIndex object from list of documents"""
    print("Building Inverteed index...", file=sys.stderr)
    index_as_dict = {}
    for document_index in documents.keys():
        words = list(set(re.split(r"\W+", documents[document_index])))
        for word in words:
            if index_as_dict.get(word) is None:
                index_as_dict[word] = [document_index]
            else:
                index_as_dict[word] = index_as_dict[word] + [document_index]
    return InvertedIndex(index_as_dict)

def setup_parser(parser):
    """Determine the set of parameters for CLI"""
    subparsers = parser.add_subparsers(help="choose command")

    build_parser = subparsers.add_parser(
        "build",
        help="read documents, build inverted index and dump it",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    build_parser.add_argument(
        "-s", "--strategy",
        help="pick the storage strategy",
        choices=['json', 'pickle'],
        default=DEFAULT_STORAGE_POLICY
    )
    build_parser.add_argument(
        "-d", "--dataset", dest="dataset_path",
        help="path to dataset to load",
        default=DEFAULT_DATASET_PATH,
    )
    build_parser.add_argument(
        "-o", "--output", dest="output_path",
        help="path to dump builded inverted index",
        default=DEFAULT_OUTPUT_PATH,
    )
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparsers.add_parser(
        "query", help="query inverted index",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    query_parser.add_argument(
        "-i", "--json-index", dest='input',
        help="path to read inverted index",
        default=DEFAULT_OUTPUT_PATH,
    )
    query_parser.add_argument(
        "-q", "--query", required=True, nargs="+",
        action="append", dest="queries",
        help="query to run against inverted index",
    )
    query_parser.set_defaults(callback=callback_query)

def callback_build(arguments):
    """Determine behaviour for BUILD command"""
    print(f"call build subcommand with arguments= {arguments}", file=sys.stderr)
    if arguments.strategy == "json":
        documents = load_documents(arguments.dataset_path)
        inverted_index = build_inverted_index(documents)
        inverted_index.dump(arguments.output_path)
    else:
        print(f"{arguments.strategy} is not implemeted yet", file=sys.stderr)

def callback_query(arguments):
    """Determine behaviour for QUERY command"""
    print(f"call query subcommand with arguments= {arguments}", file=sys.stderr)
    inverted_index = InvertedIndex.load(arguments.input)
    for query in arguments.queries:
        document_ids = inverted_index.query(query)
        print(",".join(map(str, document_ids)))

def main():
    """Main function"""
    parser = ArgumentParser(
        prog="inverted-index",
        description="(Inverted Index CLI) Tool to build, dump, load \
                     and query inverted index",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    # print(arguments, file = sys.stderr)

    arguments.callback(arguments)

if __name__ == "__main__":
    main()
