import os
import sys
import logging
import argparse
import configparser

from log_analyzer.parser import Parser


def argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config', type=str, help='config file path',
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.ini'))
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
    try:
        parser = Parser()
        parser.parse(log_dir=config['LOG_DIR'], report_dir=config['REPORT_DIR'])
        parser.generate_report(report_size=config['REPORT_SIZE'])
    except Exception as e:
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()

