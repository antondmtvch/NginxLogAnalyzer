import os
import sys
import configparser
import argparse
import logging
from log_analyzer.parser import Parser

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def set_logging_filename(filename=None) -> None:
    logging.basicConfig(
        format='[%(asctime)s] %(levelname).1s %(message)s',
        level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S', filename=filename
    )


def argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config', type=str,
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.ini'),
                        help='Путь к файлу с конфигом.')
    return parser.parse_args()


def update_default_config(default: dict) -> None:
    args = argument_parser()
    parser = configparser.ConfigParser()
    parser.optionxform = str

    with open(args.config, 'r', encoding='utf-8') as f:
        parser.read_file(f)

    other = parser['CONFIG'] if 'CONFIG' in parser.sections() else {}
    default.update(other)
    set_logging_filename(default.get('LOG_FILE'))


def main(_config: dict) -> None:
    try:
        update_default_config(_config)
        parser = Parser()
        parser.parse(log_dir=_config['LOG_DIR'], report_dir=_config['REPORT_DIR'])
        parser.generate_report(report_size=_config['REPORT_SIZE'])
    except Exception as e:
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main(config)

