import calendar
import datetime


class Report(object):
    def __init__(self, year, month, time_diff=3600 * 4):
        self.year = year
        self.month = month
        self.time_diff = time_diff
        self.days = {}

    def add(self, day):
        assert self.year == day.year and self.month == day.month
        self.days[day.day] = day

    def get_line_info(self, i, width):
        return f"{width // 60}:{width % 60:02} ({(i - width) // 60:02}:{(i - width) % 60:02} - {i // 60:02}:{i % 60:02})"

    def get_detail_info(self, s, e):
        i = e // 60
        width = (e - s) // 60
        return self.get_line_info(i, width)

    def draw_active_line(self, detail):
        line = [0 for _ in range(1440)]
        for d in detail:
            s = int((d[0] % 86400) / 60)
            e = int((d[1] % 86400) / 60)
            for i in range(s, e + 1):
                line[i] = 1
        text = ""
        width = 0
        type = 0
        line.append(-1)
        for i, l in enumerate(line):
            if l == type:
                width += 1
            else:
                if type > 0:
                    color = "green"
                else:
                    color = "#e8e8e8"
                text += f"<div title='{self.get_line_info(i, width)}' style='margin:1 0 1 0;display:inline-block;height:20px;width:{width}px;background:{color}'>&nbsp;</div>"
                width = 1
                type = l
        return text

    def draw_details(self, details):
        if len(details) == 0:
            return ''
        maximum = max([d[1] - d[0] for d in details])
        text = ""
        for d in details:
            s = int(d[0] % 86400)
            e = int(d[1] % 86400)
            if e < s:
                continue
            width = int(670 * (e - s) / maximum)
            text += f"<div style='background:#c8c8c8;padding:5px;margin:5px;width:680px'>{self.get_detail_info(s, e)}<br><div style='width:{width}px;padding:2px;overflow:visible;background:gray;color:white'>{(e - s) / 60:0.1f}&nbsp;M</div><div style='width:680px;height:40px;overflow:hidden'>{' | '.join([str(d) for d in d[2:]])}</div></div>"
        return text

    def draw_process(self, width, color, hours, data):
        return f"<div style='background:#c8c8c8;padding:5px;margin:5px;width:680px'><div style='width:{width}px;padding:2px;overflow:visible;background:{color};color:white'>{hours:0.1f}&nbsp;H</div><div style='width:680px;height:40px;overflow:hidden'>{data}</div></div>"

    def draw_sorted(self, processes):
        if len(processes) == 0:
            return ''
        maximum = processes[0][1]
        text = ""
        for k, v in [(k, v) for k, v in processes]:
            color = 'green'
            if k[0] == '-':
                color = 'red'
            if k[0] == '0':
                color = 'gray'
            text += self.draw_process(int(670 * v / maximum), color, v / 3600, k[k.find('|') + 1:])
        return text

    def draw_calendar(self, x, y, day_width=50, day_height=50, day_margin=5):
        num = calendar.monthrange(self.year, self.month)[1]
        add = y + day_height + day_margin
        text = f"<div onclick='set_day(0)' style='background:#d1d1f7;display:block;position:absolute;top:{y}px;left:{x}px;width:{(day_width + day_margin) * 7 - day_margin}px;height:{day_height}px;border:1px solid gray'>{self.year}-{self.month}</div>"
        lines = ""
        for d in range(1, num + 1):
            date = datetime.datetime(self.year, self.month, d)
            left = date.weekday() * (day_width + day_margin) + x
            top = add
            if date.weekday() == 6:
                add += day_height + day_margin
            if d not in self.days:
                color = "#d1d1f7"
                work = 0
                active = 0
                details = []
                processes = []
            else:
                day = self.days[d]
                report = day.report()
                active = report['active'] / 3600
                color = report['color']
                work = report['work'] / 3600
                details = report['details']
                processes = sorted([(k, v) for k, v in report['process_time'].items()], key=lambda k: k[1],
                                   reverse=True)
            text += f"<div onclick='set_day({d})' style='background:{color};display:block;position:absolute;top:{top}px;left:{left}px;width:{day_width}px;height:{day_height}px;border:1px solid gray'>{d}<br>{work:0.1f}</div>"
            text += f"<div id='day{d}' style='display:none;width:1500px;position:absolute;top:{day_margin}px;left:{7 * (day_width + day_margin) + x}px'>"
            text += f"{self.year}-{self.month:02}-{d:02}<hr>Active time: {active:0.1f} H<br>Work time: {work:0.1f} H<br>"
            line = self.draw_active_line(details)
            text += line
            lines += line + "<br>"
            text += f"<div style='display:block;width:710px;margin:5px;float:left;overflow-y:scroll;height:840px'>{self.draw_sorted(processes)}</div>"
            text += f"<div style='display:block;width:710px;margin:5px;float:left;overflow-y:scroll;height:840px'>{self.draw_details(details)}</div>"
            text += "</div>"
        text += f"<div id='day0' style='display:none;width:1500px;position:absolute;top:{day_margin}px;left:{7 * (day_width + day_margin) + x}px'>{lines}</div>"
        return text

    def draw(self):
        num = str(calendar.monthrange(self.year, self.month)[1])
        text = ""
        text += f"<html><head><title>{self.year}-{self.month}</title>"
        text += "<script>function set_day(day){for(i=0;i<=" + num + ";i++){document.getElementById('day'+i).style.display='none';} document.getElementById('day'+day).style.display='block';}</script>"
        text += f"</head><body>{self.draw_calendar(2, 2)}</body></html>"
        return text
