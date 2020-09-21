import re
import gzip
import json
import logging
from os import path, listdir
from itertools import chain
from string import Template
from datetime import datetime
from statistics import median
from typing import Union, List, Dict
from collections import namedtuple, Counter, defaultdict

TEMPLATE_PATH = path.join(path.dirname(path.abspath(__file__)), 'template', 'report.html')

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
        return File(path=path.join(log_dir, match.group('name')), date=date, ext=match.group('ext'),
                    report_path=path.join(report_dir, f'report-{date.strftime("%Y.%m.%d")}.html'))
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


def analyze(file: File, err_threshold=10.0) -> tuple:
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

    if check_percent_of_errors(error_count=error_count, total_lines=total_lines, threshold=err_threshold):
        return request_count, request_times
    else:
        return ()


def check_percent_of_errors(error_count: int, total_lines: int, threshold: float) -> bool:
    if (error_pct := 100 * error_count / total_lines) >= threshold:
        logging.error(f'Error threshold exceeded. Error count: {error_count}. Error percent: {error_pct :.2f}%. '
                      f'Threshold: {threshold}')
        return False
    return True


def generate_table_rows(request_count: Counter, request_times:defaultdict) -> List[Dict]:
    table_rows = []
    time_total = sum(chain(*request_times.values()))
    count_total = sum(request_count.values())

    for url, times in request_times.items():
        count = request_count[url]
        times = request_times[url]
        time_sum = sum(times)

        table_rows.append({'count': count,
                           'url': url,
                           'count_perc': round(100 * count / count_total, 2),
                           'time_perc': round(100 * time_sum / time_total, 2),
                           'time_sum': round(time_sum, 2),
                           'time_avg': round(sum(times) / len(times), 2),
                           'time_max': round(max(times), 2),
                           'time_med': round(median(times), 2)})

    table_rows = sorted(table_rows, key=lambda x: x['time_sum'], reverse=True)
    return table_rows


def substitute_template(template_path: str, table_json: json) -> str:
    with open(template_path) as tmpl:
        template = Template(tmpl.read()).safe_substitute(table_json=table_json)
    return template


def save_report(report_path: str, template: str) -> None:
    with open(report_path, 'w') as report:
        report.write(template)
    logging.info(f'Report is created: {report_path}')


def generate_report(file: File, report_size: int) -> None:
    if result := analyze(file):
        count, times = result
        rows = generate_table_rows(request_count=count, request_times=times)
        table_json = json.dumps(rows[:report_size])
        template = substitute_template(template_path=TEMPLATE_PATH, table_json=table_json)
        save_report(report_path=file.report_path, template=template)
