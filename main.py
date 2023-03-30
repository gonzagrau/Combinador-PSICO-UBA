weekdays_set = {'LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO'}

class Time(object):
    def __init__(self, time_str):
        time_str = time_str.strip()
        assert len(time_str) > 3, f'time_str too short, len == {len(time_str)}'
        try:
            hh = int(time_str[:2])
            mm = int(time_str[-2:])
        except ValueError:
            raise ValueError("Invalid hour or minutes")
        assert hh//24 == 0 and hh >= 0, f'Hour must be in range(24), got hour == {hh}'
        assert mm//60 == 0 and mm >= 0, f'Minutes must be in range(60), got minutes == {mm}'

        self.hour = hh
        self.minutes = mm

    def __add__(self, other):
        raw_minute_sum = self.minutes + other.minutes
        hour_sum = (self.hour + other.hour + raw_minute_sum//60)%24
        minute_sum = raw_minute_sum%60
        return Time(f"{hour_sum:02d}:{minute_sum:02d}")

    def __sub__(self, other):
        raw_minute_sub = self.minutes - other.minutes
        hour_sub = (self.hour - other.hour - raw_minute_sub//60) % 24
        minute_sub = raw_minute_sub % 60
        return Time(f"{hour_sub:02d}:{minute_sub:02d}")

    def __eq__(self, other):
        return self.hour == other.hour and self.minutes == other.minutes

    def __str__(self):
        return f"{self.hour:02d}:{self.minutes:02d}"

    def __lt__(self, other):
        return self.hour < other.hour or (self.hour == other.hour and self.minutes < other.minutes)

    def __le__(self, other):
        return  self < other or self == other

    def __int__(self):
        return self.hour

    def __float__(self):
        return self.hour + self.minutes/60


class Course_block(object):
    def __init__(self, weekday, start_time, end_time):
        for x in start_time, end_time:
            assert isinstance(x, Time), 'Invalid start or end time'
        assert start_time < end_time, 'Start time should be smaller than endtime'
        weekday = weekday.upper()
        assert weekday in weekdays_set, 'Invalid weekday'
        self.weekday = weekday
        self.start_time = start_time
        self.end_time = end_time

    def __eq__(self, other):
        return self.weekday == other.weekday and self.start_time == other.start_time and self.end_time == other.end_time

    def __str__(self):
        return f"{self.weekday}\n{self.start_time} - {self.end_time}"

    def time_interval(self):
        return self.end_time - self.start_time

    def collides_with(self, other):
        if self.weekday != other.weekday:
            return False
        return other.start_time <= self.start_time < other.end_time \
               or self.start_time <= other.start_time < self.end_time


class Comission(object):
    def __init__(self, id, *blocks):
        assert type(id) == str, 'Invalid comission id'
        self.id = id
        self.block_list = []
        for block in blocks:
            assert isinstance(block, Course_block), 'Invalid course block'
            self.block_list.append(block)

    def __eq__(self, other):
        return self.id == other.id and self.block_list == other.block_list

    def __str__(self):
        string_rep = self.id + '\n'
        for block in self.block_list:
            string_rep += str(block) + '\n'
        return string_rep

    def collides_with(self, other):
        for sblock in self.block_list:
            for oblock in other.block_list:
                if sblock.collides_with(oblock):
                    return True
        return False



def main():
    stb1 = Time("14:00")
    etb1 = Time("16:00")
    block_1 = Course_block("lunes", stb1, etb1)
    stb2 = Time("16:00")
    etb2 = Time("17:00")
    block_2 = Course_block("lunes", stb2, etb2)
    print(block_1.collides_with(block_2))


if __name__ == '__main__':
    main()

