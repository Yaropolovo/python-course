"""Module for Inverted Index"""
from __future__ import annotations
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from typing import Dict, List
from io import TextIOWrapper
import sys
import re
import json
import pathlib
from struct import pack, unpack, calcsize

DEFAULT_DATASET_PATH = "./wikipedia_sample"
DEFAULT_OUTPUT_PATH = "./inverted_index"
DEFAULT_STORAGE_POLICY = "struct"

class InvertedIndex:
    """Class for realization of Inverted Index (and relevant methods)"""
    def __init__(self, index_as_dict: Dict[str, list]):
        """Initialization by data as a dict"""
        self.data = index_as_dict

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        # from pdb import set_trace; set_trace()
        assert isinstance(words, list)
        if len(words) == 0:
            found_documents = []
        else:
            found_documents = self.data.get(words[0], [])
            for word in words[1:]:
                list_for_word = self.data.get(word, [])
                found_documents = list(set(found_documents) & set(list_for_word))
        return found_documents

    def dump(self, filepath: str, strategy: str) -> None:
        """Save data into json"""
        print(f"Dumping inverted index into {filepath}...", file=sys.stderr)

        pathlib_filepath = pathlib.Path(filepath)
        pathlib_filepath.parent.mkdir(parents=True, exist_ok=True)

        # from pdb import set_trace; set_trace()
        if strategy == 'json':
            with open(filepath, 'w') as fout:
                json.dump(self.data, fout)
        elif strategy == 'struct':
            pairs, values = [], []

            for key, value in self.data.items():
                pairs.append([key, len(value)])
                values.extend(value)  # List[int]
            header = json.dumps(pairs).encode()
            meta = len(header)

            with open(filepath, "wb") as fout:
                fout.write(pack('I', meta))
                fout.write(pack(f'{meta}s', header))
                fout.write(pack(f'{len(values)}H', *values))
        else:
            print(f"{strategy} strategy is not implemeted yet", file=sys.stderr)

    @classmethod
    def load(cls, filepath: str, strategy: str) -> InvertedIndex:
        """Load data from file"""
        if strategy == "json":
            with open(filepath, 'r') as fin:
                loaded_dict = json.load(fin)
            return InvertedIndex(loaded_dict)
        elif strategy == "struct":
            with open(filepath, 'rb') as fin:
                fileContent = fin.read()
                meta_size = calcsize('I')
                header_size, = unpack('I', fileContent[:meta_size])
                header, = unpack(f'{header_size}s', fileContent[meta_size:(header_size+meta_size)])
                pairs = json.loads(header.decode())
                body = fileContent[(header_size+meta_size):]
                loaded_dict = {}
                for pair in pairs:
                    uns_short_size = 2
                    if pair[1] == 1:
                        element, = unpack(f"{pair[1]}H", body[:uns_short_size*pair[1]])
                        loaded_dict[pair[0]] = [element]
                    else:
                        element = unpack(f"{pair[1]}H", body[:uns_short_size*pair[1]])
                        loaded_dict[pair[0]] = list(element)
                    body = body[uns_short_size*pair[1]:]
                # from pdb import set_trace; set_trace()
            return InvertedIndex(loaded_dict)
        else:
            print(f"{strategy} strategy is not implemeted yet", file=sys.stderr)
            return None

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
        choices=['json', 'struct'],
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
        "-i", "--index", dest='input',
        help="path to read inverted index",
        default=DEFAULT_OUTPUT_PATH,
    )
    query_parser.add_argument(
        "-s", "--strategy",
        help="pick the storage strategy",
        choices=['json', 'struct'],
        default=DEFAULT_STORAGE_POLICY
    )
    query_source_group = query_parser.add_mutually_exclusive_group(required=True)
    query_source_group.add_argument(
        "-q", "--query", nargs="+",
        action="append", dest="queries",
        help="queries to run against inverted index",
    )
    query_source_group.add_argument(
        "--query-file-cp1251", dest="query_fileio",
        type=FileType("r", encoding="cp1251"),
        help="file with queries in cp1251"
    )
    query_source_group.add_argument(
        "--query-file-utf8", dest="query_fileio",
        type=FileType("r", encoding="utf-8"),
        help="file with queries in utf-8"
    )
    query_parser.set_defaults(callback=callback_query)


def callback_build(arguments):
    """Determine behaviour for BUILD command"""
    print(f"call build subcommand with arguments= {arguments}", file=sys.stderr)
    process_build(arguments.strategy, arguments.dataset_path, arguments.output_path)

def process_build(strategy, dataset_path, output_path):
    """Method to run (and test) build functionality"""
    documents = load_documents(dataset_path)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(output_path, strategy)

def callback_query(arguments) -> None:
    """Determine behaviour for QUERY command"""
    print(f"call query subcommand with arguments= {arguments}", file=sys.stderr)
    process_query(arguments.input, arguments.strategy, arguments.queries, arguments.query_fileio)

def process_query(input_path: str, strategy: str, queries_str: List[List[str]],
                  query_fileio: TextIOWrapper) -> None:
    """Method to run (and test) query functionality"""
    inverted_index = InvertedIndex.load(input_path, strategy)
    if queries_str:
        queries = queries_str
    else:
        lines = query_fileio.read().strip().split('\n')
        queries = []
        for line in lines:
            queries.append(list(set(re.split(r"\W+", line))))
    make_query_for_requested_words(inverted_index, queries)

def make_query_for_requested_words(inverted_index: InvertedIndex, queries: List[List[str]]) -> None:
    """Run queries against Index and print output to console"""
    for query in queries:
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
    arguments.callback(arguments)

if __name__ == "__main__":
    main()
