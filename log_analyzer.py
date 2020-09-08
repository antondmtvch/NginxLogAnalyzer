import os
import sys
import configparser
import argparse
from log_analyzer.parser import Parser


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def config_parser(path: str) -> dict:
    conf = configparser.ConfigParser()
    conf.optionxform = str
    conf.read(path)
    return conf['CONFIG']


def argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config', type=str,
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.ini'),
                        help='Путь к файлу с конфигом.')

    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f'Файл {args.config} не существует.')
        sys.exit(1)
    return args


def update_default_config(default: dict) -> None:
    args = argument_parser()
    other = config_parser(args.config)
    default.update(other)


def main() -> None:
    update_default_config(config)
    parser = Parser()
    parser.parse(log_dir=config['LOG_DIR'], report_dir=config['REPORT_DIR'])
    parser.generate_report(report_size=config['REPORT_SIZE'])


if __name__ == "__main__":
    main()
