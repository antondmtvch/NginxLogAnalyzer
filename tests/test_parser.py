import os
import shutil
import unittest
import random
import tempfile
import logging

from os import path
from datetime import datetime
from log_analyzer.parser import Parser

logging.basicConfig(level=logging.INFO)


class ParserTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp_dir1 = tempfile.mkdtemp()
        self.tmp_dir2 = tempfile.mkdtemp()
        self.parser = Parser()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir1)
        shutil.rmtree(self.tmp_dir2)

    def test_empty_directory(self):
        with self.assertRaises(SystemExit) as se:
            self.parser.parse(self.tmp_dir1, self.tmp_dir2)
        self.assertEqual(se.exception.code, 0)

    def test_log_not_exist(self):
        open(path.join(self.tmp_dir1, 'data.log'), 'w').close()
        open(path.join(self.tmp_dir2, 'nginx.log'), 'w').close()
        with self.assertRaises(SystemExit) as se:
            self.parser.parse(self.tmp_dir1, self.tmp_dir2)
        self.assertEqual(se.exception.code, 0)

    def test_report_exist(self):
        open(path.join(self.tmp_dir1, 'nginx-access-ui.log-20170630'), 'w').close()
        open(path.join(self.tmp_dir2, 'report-2017.06.30.html'), 'w').close()
        with self.assertRaises(SystemExit) as se:
            self.parser.parse(self.tmp_dir1, self.tmp_dir2)
        self.assertEqual(se.exception.code, 0)

    def test_find_last_file_1(self):
        self.parser.log_dir = self.tmp_dir1
        self.parser.report_dir = self.tmp_dir2

        for day in range(1, 10):
            open(path.join(self.tmp_dir1, f'nginx-access-ui.log-2017062{day}'), 'w').close()
        self.parser._find_last_file()

        last_file = self.parser.last_file
        self.assertEqual(last_file.path, path.join(self.tmp_dir1, 'nginx-access-ui.log-20170629'))
        self.assertEqual(last_file.report_path, path.join(self.tmp_dir2, 'report-2017.06.29.html'))
        self.assertEqual(last_file.date, datetime.strptime('20170629', '%Y%m%d'))
        self.assertEqual(last_file.extension, '')

    def test_find_last_file_2(self):
        self.parser.log_dir = self.tmp_dir1
        self.parser.report_dir = self.tmp_dir2

        for day in range(1, 10):
            open(path.join(self.tmp_dir1, f'BAD-NAME-log-2017062{day}'), 'w').close()
        self.parser._find_last_file()
        self.assertEqual(self.parser.last_file, None)

    def test_calculate_percent_of_errors(self):
        self.parser.reading_lines_count = 100
        self.parser.err_count = 50
        self.assertEqual(self.parser._percent_of_errors(), 50)

    def test_counters_1(self):
        with open(path.join(self.tmp_dir1, f'nginx-access-ui.log-20170620'), 'w') as log:
            log.writelines([f'Bad line {i}\n' for i in range(10)])
        self.parser.parse(self.tmp_dir1, self.tmp_dir2)

        self.assertEqual(self.parser.err_count, 10)
        self.assertEqual(self.parser.reading_lines_count, 10)

    def test_counters_2(self):
        with open(path.join(self.tmp_dir1, f'nginx-access-ui.log-20170620'), 'w') as log:
            log.writelines([f'Bad line {i}\n' for i in range(10)])
            log.write('1.194.135.240 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/group HTTP/1.1" 200 22 "-" "-" '
                      '"-" "-" "-" 0.068\n')
            log.write('1.194.135.240 -  - [29/Jun/2017:03:50:23 +0300] "POST /api/v2 HTTP/1.1" 200 22 "-" "-" '
                      '"-" "-" "-" 0.068\n')
        self.parser.parse(self.tmp_dir1, self.tmp_dir2)
        self.assertEqual(self.parser.err_count, 10)
        self.assertEqual(self.parser.reading_lines_count, 12)

    def test_threshold(self):
        self.parser.err_threshold = 30
        self.parser.err_count = 40
        self.parser.reading_lines_count = 100
        with self.assertRaises(SystemExit) as se:
            self.parser.generate_report(100)
        self.assertEqual(se.exception.code, 1)

    def test_generate_report(self):
        with open(path.join(self.tmp_dir1, f'nginx-access-ui.log-20170620'), 'w') as log:
            for _ in range(100):
                url = random.choice(['/api/v2/internal', '/export/app-install', '/api/v2/target', '/api/v2/banner'])
                time = round(random.random(), 3)
                log.write(f'1.1.1.1 -  - [-] "GET {url} HTTP/1.1" 200 22 "-" "-" "-" "-" "-" {time}\n')
        self.parser.parse(self.tmp_dir1, self.tmp_dir2)
        self.parser.generate_report(100)
        self.assertIn('report-2017.06.20.html', os.listdir(self.parser.report_dir))


if __name__ == '__main__':
    unittest.main()