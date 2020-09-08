import statistics
from collections import Counter, defaultdict


class Analyzer:
    def __init__(self):
        self.url_count = Counter()
        self.url_times = defaultdict(list)
        self.total_time = 0

    def update(self, url: str, time: float) -> None:
        """Обновить счетчик URL'а в self._url_count и добавить $request_time в self._url_times.

        :param url:
        :param time:
        :return:
        """
        self.url_count.update([url])
        self.url_times[url].append(time)
        self.total_time += time

    def count(self, url: str) -> int:
        """Сколько раз встречается URL, абсолютное значение.

        :param url: Целевой URL.
        :return: int
        """
        return self.url_count[url]

    def count_perc(self, url: str) -> float:
        """Сколько раз встречается URL, в процентнах относительно общего числа запросов.

        :param url: Целевой URL.
        :return: float
        """
        return 100 * self.count(url) / self.total_time

    def time_sum(self, url: str) -> int:
        """Суммарный $request_time для данного URL'а, абсолютное значение.

        :param url: Целевой URL.
        :return: int
        """
        return abs(sum(self.url_times[url]))

    def time_perc(self, url: str) -> float:
        """Суммарный $request_time для данного URL'а, в процентах относительно общего $request_time всех запросов.

        :param url: Целевой URL.
        :return: float
        """
        return 100 * self.time_sum(url) / self.total_time

    def time_avg(self, url: str) -> float:
        """Средний $request_time для данного URL'а.


        :param url: Целевой URL.
        :return: float
        """
        return statistics.mean(self.url_times[url])

    def time_max(self, url: str) -> int:
        """Максимальный $request_time для данного URL'а.

        :param url: Целевой URL.
        :return: int
        """
        return max(self.url_times[url])

    def time_med(self, url: str) -> float:
        """Медиана $request_time для данного URL'а.

        :param url: Целевой URL.
        :return: float
        """
        return statistics.median(self.url_times[url])
