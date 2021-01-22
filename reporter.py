import datetime
import json
import os
import time
import requests

from statistics.Report import Report
from statistics.Searcher import Searcher
from statistics.Day import Day


def main():
    buffer = []
    buffer_last_active = []
    files = os.listdir("logs")
    all_data = []
    time_min = time.time()
    time_max = 0
    time_diff = 3600*4
    print("PARSING")
    for file in sorted(files):
        print(file)
        for line in open(os.path.join("logs", file), 'r', encoding='utf8').readlines():
            data = json.loads(line)
            if data['data'] == '@active':
                data['data'] = [None, None, None]
            elif data['data'] == '@inactive':
                data['data'] = [None, None, None]
                data['status'] = not data['status']
            elif data['data'] != [None, None, None]:
                data['data'][-1] = ' '.join(data['data'][-1])
            else:
                for b in buffer:
                    b.append(b[-1])
                    time_max = max(time_max, b[-1])
                    time_min = min(time_min, b[-2])
                    all_data.append(b)
                buffer = []
            if data['data'] == [None, None, None]:
                copy = buffer
                buffer = []
                for b in copy:
                    if data['status'] is False:
                        b.append(data['time'])
                        buffer_last_active = b[:3]
                        time_max = max(time_max, b[-1])
                        time_min = min(time_min, b[-2])
                        all_data.append(b)
                    else:
                        if len(buffer_last_active) == 3:
                            buffer_last_active.append(data['time'])
                            buffer.append(buffer_last_active)
                            buffer_last_active = []
                        else:
                            assert len(buffer_last_active) == 0
            else:
                copy = buffer
                buffer = []
                for b in copy:
                    if b[0] == data['data'][0] and b[1] == data['data'][1] and b[2] == data['data'][2]:
                        if data['status'] is False:
                            b.append(data['time'])
                            all_data.append(b)
                    else:
                        buffer.append(b)
                if data['status'] is True:
                    data['data'].append(data['time'])
                    buffer.append(data['data'])
    print("ANALYZE")
    days = []
    for t in range(int(time_min + time_diff), int(time_max + time_diff) + 86400, 86400):
        dt = datetime.datetime.utcfromtimestamp(t)
        days.append(Day(dt.year, dt.month, dt.day))
    s = Searcher()
    for d in all_data:
        for day in days:
            day.add(s, d[1], d[0], d[2], d[3], d[4])
    print("RESULT")
    reports = {}
    for day in days:
        report_name = f"reports/{day.year}-{day.month}.html"
        if report_name not in reports:
            reports[report_name] = Report(day.year, day.month)
        reports[report_name].add(day)
    for k, v in reports.items():
        with open(k, 'w', encoding='utf8') as f:
            f.write(v.draw())


if __name__ == '__main__':
    try:
        main()
        requests.post("http://127.0.0.1:9020/", json={'title': 'Time Tracker', 'text': 'Отчёт переформирован'})
    except Exception as _:
        requests.post("http://127.0.0.1:9020/", json={
            'title': 'Time Tracker',
            'text': 'Формирование отчёта завершилось с ошибкой!',
            'timeout': 86400
        })