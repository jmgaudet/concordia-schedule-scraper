import calendar
import datetime
import re

import icalendar
from dateutil import parser

regex = re.compile(r'([a-zA-Z]{2,4}) (.*) - (.*)')


class ScheduledCourse:
    """A class used to organize and parse the given course information from a dict to a usable object"""

    def __init__(self, name, number, section, component, times, room, instructor, start_end):
        self.component = component
        title = name.split(' -')
        self.name = title[0] + title[1].title() + ' (' + self.component[:3] + ')'
        self.description = 'Number: {}\nSection: {}\nInstructor: {}'.format(number, section, instructor)
        self.section = section
        self.times = times
        self.room = room
        self.start_end = start_end
        days, startt, endt = regex.match(times).groups()
        start_day, end_day = [n.strip() for n in start_end.split('-')]
        formatted_start_day = datetime.datetime.strptime(start_day, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.start_time = parser.parse('{} {} EDT'.format(startt, formatted_start_day))
        first_day = days[0:2].lower()
        while calendar.day_name[self.start_time.weekday()].lower()[0:2] != first_day:
            self.start_time += datetime.timedelta(days=1)
        self.end_time = parser.parse('{} {} EDT'.format(endt, self.start_time.date().isoformat()))
        fdays = []
        for x in range(int(len(days) / 2)):
            fdays.append(days[x * 2:x * 2 + 2])
        self.repeat_rule = {'freq': 'weekly', 'count': 13, 'byday': fdays}

    def create_ical_event(self):
        event = icalendar.Event()
        event.add('summary', u'{}'.format(self.name))
        event.add('location', self.room)
        event.add('dtstart', self.start_time)
        event.add('dtend', self.end_time)
        event.add('description', self.description)
        event.add('rrule', self.repeat_rule)
        return event

    def __str__(self):
        """Allows for ease of reading (debugging) of the object"""
        return 'Name: ' + self.name + \
               '\nDescription: ' + self.description + \
               '\nComponent: ' + self.component + \
               '\nTimes ' + self.times + \
               '\nLocation: ' + self.room + \
               '\nRepeat Rule: ' + str(self.repeat_rule)
