import json
import re


class Searcher(object):
    def __init__(self):
        self.filters = sorted(json.load(open('filters.json', 'r', encoding='utf8')), key=lambda p: p['priority'])
        self.objects = json.load(open('objects.json', 'r', encoding='utf8'))
        self.count = 0

    def check(self, f, filter, data):
        return f not in filter or filter[f] == data or (filter[f] is not None and re.match(re.compile(filter[f]), data))

    def search(self, process, cmd, title):
        self.count += 1
        for filter in self.filters:
            if self.check('process', filter, process):
                if self.check('cmd', filter, cmd):
                    if self.check('title', filter, title):
                        return self.objects[filter['object']]
        print('process', process)
        print('cmd', cmd)
        print('title', title)
        raise Exception(f"Data not found after {self.count - 1} processed")
