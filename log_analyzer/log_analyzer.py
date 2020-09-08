from .parser import Parser

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def main():
    parser = Parser()
    parser.parse(log_dir=config['LOG_DIR'], report_dir=config['REPORT_DIR'])
    parser.generate_report(report_size=config['REPORT_SIZE'])


if __name__ == "__main__":
    main()
