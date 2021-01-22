import json
import subprocess
import re
import time
from datetime import datetime
from threading import Thread, Lock

import psutil as psutil
from pynput import mouse, keyboard

LOCK = Lock()


def log(res, t, status):
    with LOCK:
        data = json.dumps({
                'time': t,
                'status': status,
                'data': res
            })
        with open(f"logs/{datetime.utcfromtimestamp(t).strftime('%Y-%m-%d')}.log", 'a+', encoding='utf8') as f:
            f.write(data + '\n')


class Tracker(Thread):
    def __init__(self):
        super().__init__()
        self.last_res = [None, None, None]
        self.is_active = False
        self.last_active = 0

    def run(self):
        while True:
            time_start = time.time()
            try:
                d = get_active_window_title()
                res = [d['name'], d['process']['name'], d['process']['cmdline']]
                if self.last_res != res:
                    log(self.last_res, time_start, False)
                    self.last_res = res
                    log(res, time_start, True)
            except Exception as e:
                print(e)
            if self.is_active and time.time() - self.last_active > 200:
                self.is_active = False
                log('@active', self.last_active, False)
            sl = 1.0 - (time.time() - time_start)
            if sl > 0:
                time.sleep(sl)

    def active(self):
        if not self.is_active:
            log('@active', time.time(), True)
            self.is_active = True
        self.last_active = time.time()


TRACKER = Tracker()


def get_active_window_title():
    root = subprocess.Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=subprocess.PIPE)
    stdout, stderr = root.communicate()

    m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)
    if m != None:
        window_id = m.group(1)
        window = subprocess.Popen(['xprop', '-id', window_id, 'WM_NAME', '_NET_WM_PID'], stdout=subprocess.PIPE)
        stdout, stderr = window.communicate()
    else:
        return None

    res = {
        'name': None,
        'process': None
    }
    for s in stdout.split(b'\n'):
        match = re.match(b"WM_NAME\(\w+\) = (?P<name>.+)$", s)
        if match != None:
            res['name'] = match.group("name").decode("utf8", errors="ignore").strip('"')
        match = re.match(b"_NET_WM_PID\(\w+\) = (?P<pid>.+)$", s)
        if match != None:
            res['process'] = psutil.Process(int(match.group("pid").decode("utf8", errors="ignore"))).as_dict()

    return res


def on_move(x, y):
    TRACKER.active()


def on_click(x, y, button, pressed):
    TRACKER.active()


def on_scroll(x, y, dx, dy):
    TRACKER.active()


def on_pressed(key):
    TRACKER.active()


def on_release(key):
    TRACKER.active()


if __name__ == "__main__":
    l1 = keyboard.Listener(on_press=on_pressed, on_release=on_release)
    l2 = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    l1.start()
    l2.start()
    TRACKER.setDaemon(True)
    TRACKER.start()
    TRACKER.join()
