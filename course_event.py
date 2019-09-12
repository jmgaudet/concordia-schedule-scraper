import calendar
import datetime
import re

import icalendar
from dateutil import parser

from quickstart import get_calendar_service

regex = re.compile(r'([a-zA-Z]{2,4}) (.*) - (.*)')


class ScheduledCourse:
    """A class used to parse the given course information from a dict to a usable object"""

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
        start_day_format = datetime.datetime.strptime(start_day, "%d/%m/%Y").strftime("%Y-%m-%d")  # 2020-01-06
        end_day_format = datetime.datetime.strptime(end_day, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.start_period = parser.parse('{} {} EDT'.format(start_day_format, startt))  # 2020-01-09 15:45:00-05:00
        # start_day_formatted must advance to the actual starting day (not simply the first day of classes):
        first_day = days[0:2].lower()
        while calendar.day_name[self.start_period.weekday()].lower()[0:2] != first_day:
            self.start_period += datetime.timedelta(days=1)
        self.end_period = parser.parse('{} {} EDT'.format(self.start_period.date().isoformat(), endt))
        until = parser.parse('{} {} EDT'.format(end_day_format, "11:55PM"))  # This is the endtime of the LAST class
        days_list = []
        for x in range(int(len(days) / 2)):
            days_list.append(days[x * 2:x * 2 + 2])
        self.repeat_rule = {'freq': 'weekly', 'until': until, 'byday': days_list}
        self.google_days_list = ','.join(days_list)
        self.google_until = re.sub(r'\W+', '', until.isoformat())

    def create_ical_event(self):
        event = icalendar.Event()
        event.add('summary', u'{}'.format(self.name))
        event.add('location', self.room)
        event.add('dtstart', self.start_period)
        event.add('dtend', self.end_period)
        event.add('description', self.description)
        event.add('rrule', self.repeat_rule)
        return event

    def create_google_event(self):
        service = get_calendar_service()
        iana_timezone = 'America/Montreal'
        service.events().insert(calendarId='primary',
                                body={
                                    'summary': u'{}'.format(self.name),
                                    'description': self.description,
                                    'location': self.room,
                                    'start': {'dateTime': self.start_period.isoformat(),
                                              'timeZone': iana_timezone},
                                    'end': {'dateTime': self.end_period.isoformat(), 'timeZone': iana_timezone},
                                    "recurrence": [
                                        "RRULE:FREQ=WEEKLY;BYDAY=" + self.google_days_list + ";UNTIL=" + self.google_until[:-4] + "Z", ]
                                }
                                ).execute()

    def __str__(self):
        return 'Name: ' + self.name + \
               '\nDescription: ' + self.description + \
               '\nComponent: ' + self.component + \
               '\nTimes: ' + self.times + \
               '\nstart_period: ' + self.start_period.isoformat() + \
               '\nend_period: ' + self.end_period.isoformat() + \
               '\nLocation: ' + self.room + \
               '\nRepeat Rule: ' + str(self.repeat_rule)
