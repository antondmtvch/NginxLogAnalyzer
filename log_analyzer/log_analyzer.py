import re
import gzip
import json
import logging
from os import path, listdir
from itertools import chain
from string import Template
from datetime import datetime
from statistics import median
from typing import Union
from collections import namedtuple, Counter, defaultdict

BASE_DIR = path.dirname(path.abspath(__file__))
TEMPLATE_PATH = path.join(BASE_DIR, 'template', 'report.html')

FILE_NAME_PATTERN = re.compile(r'^(?P<name>nginx-access-ui\.log-(?P<date>\d{8})(?P<ext>\.gz|))$')
LINE_PATTERN = re.compile(
    r'^.+\[.+\]\s\"(?:GET|POST|HEAD|PUT|OPTIONS)\s(?P<url>.+?)\sHTTP.+?\".+\s(?P<request_time>\d+\.\d+)$'
)

File = namedtuple('LogFile', ['path', 'date', 'ext', 'report_path'])


def find_log_file(log_dir: str, report_dir: str) -> Union[File, None]:
    try:
        if not (files := listdir(log_dir)):
            logging.info(f"{log_dir} directory is empty!")
            return None
    except FileNotFoundError as err:
        logging.exception(err)
        return None

    match, date = None, datetime.utcfromtimestamp(0)

    for fname in files:
        if mch := re.match(FILE_NAME_PATTERN, fname):
            try:
                if (dt := datetime.strptime(mch.group('date'), '%Y%m%d')) > date:
                    match, date = mch, dt
            except ValueError as err:
                logging.exception(err)

    if match:
        report_path = path.join(report_dir, f'report-{date.strftime("%Y.%m.%d")}.html')
        log_path = path.join(log_dir, match.group('name'))
        return File(path=log_path, date=date, ext=match.group('ext'), report_path=report_path)
    else:
        logging.info(f'the directory {log_dir} does not contain files with logs of the required format!')
        return None


def parse_lines(file: File) -> tuple:
    reader = gzip.open if file.ext == '.gz' else open
    with reader(file.path, 'rt', encoding='utf-8') as f:
        for line in f:
            if match := re.match(LINE_PATTERN, line):
                url, time = match.groups()
                yield url, float(time)
            else:
                yield ()


def generate_report(file: File, report_size: int) -> None:
    if path.exists(file.report_path):
        logging.info(f'Report already exists: {file.report_path}')
        return None

    request_count = Counter()
    request_times = defaultdict(list)
    error_count = total_lines = 0

    for line in parse_lines(file):
        if line:
            url, time = line
            request_count.update([url])
            request_times[url].append(time)
        else:
            error_count += 1
        total_lines += 1

    if (error_pct := 100 * error_count / total_lines) >= 30:
        logging.error(f'Error threshold exceeded. Error count: {error_count}. Error percent: {error_pct :.2f}%')
        return None

    table_json = []
    time_total = sum(chain(*request_times.values()))
    count_total = sum(request_count.values())

    for url, times in request_times.items():
        count = request_count[url]
        times = request_times[url]
        time_sum = sum(times)

        table_json.append({'count': count,
                           'url': url,
                           'count_perc': round(100 * count / count_total, 2),
                           'time_perc': round(100 * time_sum / time_total, 2),
                           'time_sum': round(time_sum, 2),
                           'time_avg': round(sum(times) / len(times), 2),
                           'time_max': round(max(times), 2),
                           'time_med': round(median(times), 2)})

    table_json = sorted(table_json, key=lambda x: x['time_sum'], reverse=True)
    table_json = json.dumps(table_json[:int(report_size)])

    with open(TEMPLATE_PATH) as tmpl:
        template = Template(tmpl.read()).safe_substitute(table_json=table_json)
    with open(file.report_path, 'w') as report:
        report.write(template)
    logging.info(f'Report is created: {file.report_path}')
