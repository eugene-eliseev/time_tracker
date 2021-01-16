import datetime


class Day(object):
    def __init__(self, year, month, day, time_diff=3600*4):
        self.details = []
        self.process_time = {}
        self.data = {}
        self.year = year
        self.month = month
        self.day = day
        self.time_diff = time_diff
        self.time_start = datetime.datetime(year, month, day).timestamp() + time_diff
        self.time_end = self.time_start + 86400

    def check(self, start_time, end_time):
        res = (max(start_time, self.time_start), min(end_time, self.time_end))
        if res[0] < res[1]:
            return res
        return None

    def add(self, searcher, process, title, cmd, start_time, end_time):
        start_time += self.time_diff
        end_time += self.time_diff
        res = self.check(start_time, end_time)
        if res is not None:
            if process is None and title is None and cmd is None:
                raise Exception("All is None!")
            else:
                action = searcher.search(process, cmd, title)
                if action['type'] not in self.data:
                    self.data[action['type']] = {'name': action['name'], 'time': 0}
                self.data[action['type']]['time'] += res[1] - res[0]
                self.details.append((res[0], res[1], process, title, cmd))
                self.add_process(start_time, end_time, process, title, cmd, action['type'])

    def add_process(self, start_time, end_time, process, title, cmd, type):
        data = ' | '.join([str(type), str(process), str(title), str(cmd)])
        if data not in self.process_time:
            self.process_time[data] = 0
        self.process_time[data] += end_time - start_time

    def report(self):
        work = sum([v['time'] for k, v in self.data.items() if k > 0])
        active = sum([v['time'] for k, v in self.data.items()])
        level = int(work / (12 * 3600 / 256))

        details = sorted(self.details, key=lambda k: k[0])

        return {
            'day': f"{self.year}-{self.month:02}-{self.day:02}",
            'color': f"#{256 - level:02x}{level:02x}00",
            'work': work,
            'active': active,
            'data': self.data,
            'details': details,
            'process_time': self.process_time
        }
