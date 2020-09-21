import sys
import logging
import argparse
import configparser
from os import path
from log_analyzer.log_analyzer import generate_report, find_log_file


def argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config', type=str, help='config file path',
                        default=path.join(path.dirname(path.abspath(__file__)), 'settings.ini'))
    return parser.parse_args()


def config_parser() -> dict:
    args = argument_parser()
    parser = configparser.ConfigParser()
    parser.optionxform = str

    with open(args.config, 'r', encoding='utf-8') as file:
        parser.read_file(file)
    return parser['CONFIG'] if 'CONFIG' in parser.sections() else {}


def main() -> None:
    config = {
        'REPORT_SIZE': 1000,
        'REPORT_DIR': './reports',
        'LOG_DIR': './log',
    }
    config.update(config_parser())
    logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s', level=logging.INFO,
                        datefmt='%Y.%m.%d %H:%M:%S', filename=config.get('LOG_FILE'))

    log_dir = path.abspath(config['LOG_DIR'])
    report_dir = path.abspath(config['REPORT_DIR'])
    try:
        if file := find_log_file(log_dir, report_dir):
            if path.exists(file.report_path):
                logging.info(f'Report already exists: {file.report_path}')
                return None
            else:
                generate_report(file=file, report_size=int(config['REPORT_SIZE']))
    except Exception as err:
        logging.exception(f'Unexpected error: {err}')
        sys.exit(1)


if __name__ == "__main__":
    main()
