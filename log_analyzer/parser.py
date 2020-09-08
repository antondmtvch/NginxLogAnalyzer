import re
import os
import sys
import gzip
import json
import logging

from typing import Union
from string import Template
from collections import namedtuple
from datetime import datetime
from log_analyzer.analyzer import Analyzer

REP_TEMPLATE_PATH = os.path.join('log_analyzer', 'template', 'report.html')
FILE_LINE_PATTERN = re.compile(r'^.+\[.+\]\s\"[A-Z]+?\s(?P<url>/.+?)\sHTTP.+?\".+\s(?P<request_time>\d+\.\d+)$')
FILE_NAME_PATTERN = re.compile(r'^(?P<name>nginx-access-ui\.log-(?P<date>\d{8})(?P<extension>\.gz|))$')


class Parser:
    def __init__(self):
        self.analyzer = Analyzer()
        self.log_dir = None
        self.last_file = None
        self.report_dir = None
        self.line_pattern = FILE_LINE_PATTERN
        self.name_pattern = FILE_NAME_PATTERN

    def parse(self, log_dir: str, report_dir: str) -> None:
        """

        :param log_dir:
        :param report_dir:
        :return:
        """
        self.report_dir = report_dir
        self.log_dir = log_dir
        self._find_last_file()

        if not self.last_file:
            logging.info(f'В директории {self.log_dir} отсутствует нужный файл с логами.')
            sys.exit(0)

        if os.path.exists(self.last_file.report_path):
            logging.info(f'Отчет {self.last_file.report_path} существует.')
            sys.exit(0)

        for line in self._read_lines():
            if m := re.match(self.line_pattern, line):
                url, time = m.groups()
                self.analyzer.update(url, float(time))

    def _find_last_file(self) -> namedtuple:
        """Поиск последнего по дате файла с логами.

        :return: None
        """
        if not (logs := os.listdir(self.log_dir)):
            logging.info(f'Директория {self.log_dir} пустая.')
            sys.exit(0)

        match = None
        date = datetime.utcfromtimestamp(0)

        for name in logs:
            if m := re.match(self.name_pattern, name):
                if (d := datetime.strptime(m.group('date'), '%Y%m%d')) > date:
                    date ,match = d, m

        File = namedtuple('File', ['path', 'date', 'extension', 'report_path'])
        report_name = f'report-{date.strftime("%Y.%m.%d")}.html'
        report_path = os.path.join(os.path.abspath(self.report_dir), report_name)

        self.last_file = File(path=os.path.join(os.path.abspath(self.log_dir), match.group('name')), date=date,
                              extension=match.group('extension'), report_path=report_path) if match else None

    def _read_lines(self) -> str:
        """Чтение строк файла.

        :return: str
        """
        reader = gzip.open if self.last_file.extension == '.gz' else open
        with reader(self.last_file.path, 'rt', encoding='utf-8') as file:
            yield from file

    def generate_report(self, report_size: Union[str, int]) -> None:

        if not isinstance(report_size, int):
            if isinstance(report_size, str) and report_size.isdigit():
                report_size = int(report_size)
            else:
                raise TypeError(f'report_size must be digit, not {report_size.__class__.__name__}.')

        top = sorted(
            map(
                lambda x: (x[0], sum(x[1])), self.analyzer.url_times.items()
            ), key=lambda x: x[1], reverse=True
        )[0:report_size]

        table_json = []
        for url, time in top:
            table_json.append(
                {
                    "count": self.analyzer.count(url),
                    "time_avg": round(self.analyzer.time_avg(url), 3),
                    "time_max": round(self.analyzer.time_max(url), 3),
                    "time_sum": round(self.analyzer.time_sum(url), 3),
                    "url": url,
                    "time_med": round(self.analyzer.time_med(url), 3),
                    "time_perc": round(self.analyzer.time_perc(url), 3),
                    "count_perc": round(self.analyzer.count_perc(url), 3),
                }
            )
        with open(REP_TEMPLATE_PATH) as report_template:
            with open(self.last_file.report_path, 'w') as report:
                template = Template(report_template.read()).safe_substitute(table_json=json.dumps(table_json))
                report.write(template)
        logging.info(f'Создан отчет: {self.last_file.report_path}')
