import datetime
import time

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 2003

def parse_logs_to_dict(logs_as_text: str, host, port):
    """Transform logs into dict format"""
    result_dict = {}
    for line in logs_as_text.split('\n'):
        if len(line.split(":"))>1:
            query = line.split(":")[1].strip()

            if (query in result_dict.keys()) and (result_dict[query][0] is not None) and \
                    (result_dict[query][1] is not None) and (result_dict[query][2] is not None):
                print_echo_by_key(result_dict, query, host, port)
                del result_dict[query]

            if query not in result_dict.keys():
                result_dict[query] = [None, None, None]

            if "start" in line:
                result_dict[query][1] = line.split(" ")[0]
            elif "found" in line:
                splitted_line = line.split(" ")
                result_dict[query][0] = int(splitted_line[1 + splitted_line.index("found")])
            else:
                result_dict[query][2] = line.split(" ")[0]
    return result_dict

def print_echo_by_key(result_dict, query_key, host, port):
    """wrapper for print_echo"""
    print_echo(result_dict[query_key][0], result_dict[query_key][1],
               result_dict[query_key][2], host, port)

def print_echo(atricle_found, start_as_str: str, finish_as_str:str, host: str, port):
    """print metrics for graphite"""
    start_time = datetime.datetime.strptime(start_as_str, "%Y%m%d_%H%M%S.%f")
    finish_time = datetime.datetime.strptime(finish_as_str, "%Y%m%d_%H%M%S.%f")
    dif = finish_time - start_time
    finish_stamp = int(time.mktime(finish_time.timetuple()))

    # from pdb import set_trace;
    # if atricle_found == 28:
    #     set_trace()
    print(f'echo "wiki_search.article_found {atricle_found} {finish_stamp}" | nc -N {host} {port}')
    print(f'echo "wiki_search.complexity {dif.total_seconds():.3f} {finish_stamp}" | nc -N {host} {port}')


def process_parser_command(source_file: str, host: str, port):
    """argument procession"""
    with open(source_file, encoding='utf-8') as fin:
        text = fin.read()

    logs_as_dict = parse_logs_to_dict(text, host, port)
    for query in logs_as_dict.keys():
        print_echo_by_key(logs_as_dict, query, host, port)

def callback_parser(arguments):
    """calback wrapper"""
    process_parser_command(arguments.process, arguments.host, arguments.port)

def setup_parser(parser: ArgumentParser):
    """Determine the set of parameters for CLI"""
    parser.add_argument(
        "--process",
        help="path to dataset to process",
    )
    parser.add_argument(
        "--host",
        help="host for graphite",
        default=DEFAULT_HOST,
    )
    parser.add_argument(
        "--port",
        help="port for graphite",
        default=DEFAULT_PORT,
    )
    parser.set_defaults(callback=callback_parser)

def main():
    """Execute 'process' command from CLI"""
    parser = ArgumentParser(
        prog="log_parser",
        description="parsing logs and prepare metrics for TSDB",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)

if __name__ == "__main__":
    main()
