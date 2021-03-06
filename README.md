# NginxLogAnalyzer

При запуске скрипт обрабатывает последний (со самой свежей датой в имени, не по **mtime** файла) лог в `LOG_DIR`, в
результате генерируется html отчет со статистикой в `REPORT_DIR`. 

Если удачно обработал, то работу не переделывает при повторном запуске. Готовые отчеты лежат в `REPORT_DIR`. В отчет
попадает `REPORT_SIZE` URL'ов с наибольшим суммарным временем обработки.

**Запуск**

Для запуска необходим `Python 3.8`.
```
$ python main.py --config [config file path]
```
По умолчанию используется конфигурация из `settings.ini`.


**Формат имени фалов**
- **plain** - `nginx-access-ui.log-20170630`
- **gzip** - `nginx-access-ui.log-20170630.gz`

**Структура отчета**
- `count` - количество запросов
- `count_perc` - количество данного URL'а, в процентнах относительно общего числа запросов
- `time_sum` - суммарный `$request_time` для данного URL'а
- `time_perc` - суммарный `$request_time` для данного URL'а, в процентах относительно общего `$request_time` всех запросов
- `time_avg` - средний `$request_time` для данного URL'а
- `time_max` - максимальный `$request_time` для данного URL'а
- `time_med` - медиана `$request_time` для данного URL'а

![report_example](https://user-images.githubusercontent.com/33620637/93717230-0add9900-fb7d-11ea-900d-abcfd7f3835d.png)
