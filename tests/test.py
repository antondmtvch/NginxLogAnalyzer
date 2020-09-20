import random
import shutil
import tempfile
import unittest

from os import path, listdir
from datetime import datetime
from log_analyzer.log_analyzer import find_log_file, generate_report


class LogAnalyzerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.log_dir = tempfile.mkdtemp()
        self.rep_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.log_dir)
        shutil.rmtree(self.rep_dir)

    def test_empty_directory(self):
        file = find_log_file(self.log_dir, self.rep_dir)
        self.assertEqual(file, None)

    def test_log_not_exist(self):
        open(path.join(self.log_dir, 'data.log'), 'w').close()
        file = find_log_file(self.log_dir, self.rep_dir)
        self.assertEqual(file, None)

    def test_find_last_file_with_correct_name(self):
        for day in range(1, 10):
            open(path.join(self.log_dir, f'nginx-access-ui.log-2017062{day}'), 'w').close()
        file = find_log_file(self.log_dir, self.rep_dir)
        self.assertEqual(file.path, path.join(self.log_dir, 'nginx-access-ui.log-20170629'))
        self.assertEqual(file.report_path, path.join(self.rep_dir, 'report-2017.06.29.html'))
        self.assertEqual(file.date, datetime.strptime('20170629', '%Y%m%d'))
        self.assertEqual(file.ext, '')

    def test_find_last_file_with_bad_name(self):
        for day in range(1, 10):
            open(path.join(self.log_dir, f'BAD-NAME-log-2017062{day}'), 'w').close()
        file = find_log_file(self.log_dir, self.rep_dir)
        self.assertEqual(file, None)

    def test_generate_report(self):
        with open(path.join(self.log_dir, f'nginx-access-ui.log-20170620'), 'w') as log:
            for _ in range(100):
                url = random.choice(['/api/v2/internal', '/export/app-install', '/api/v2/target', '/api/v2/banner'])
                time = round(random.random(), 3)
                log.write(f'1.1.1.1 -  - [-] "GET {url} HTTP/1.1" 200 22 "-" "-" "-" "-" "-" {time}\n')
        file = find_log_file(self.log_dir, self.rep_dir)
        generate_report(file=file, report_size=100)
        self.assertIn('report-2017.06.20.html', listdir(self.rep_dir))


if __name__ == '__main__':
    unittest.main()
