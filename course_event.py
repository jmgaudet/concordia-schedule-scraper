import calendar
import datetime
import re

import icalendar
from dateutil import parser
from quickstart import get_calendar_service

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
        formatted_start_day = datetime.datetime.strptime(start_day, "%d/%m/%Y").strftime("%Y-%m-%d")  # 2020-01-06
        self.start_time = parser.parse('{} {} EDT'.format(startt, formatted_start_day))  # 2020-01-09 15:45:00-05:00
        first_day = days[0:2].lower()
        while calendar.day_name[self.start_time.weekday()].lower()[0:2] != first_day:
            self.start_time += datetime.timedelta(days=1)
        self.end_time = parser.parse('{} {} EDT'.format(endt, self.start_time.date().isoformat()))

        fdays = []
        for x in range(int(len(days) / 2)):
            fdays.append(days[x * 2:x * 2 + 2])
        self.repeat_rule = {'freq': 'weekly', 'count': 13, 'byday': fdays}
        print(str(fdays))

        fast_forward = datetime.timedelta(weeks=13)
        g_end_time = datetime.datetime.strptime(formatted_start_day, "%Y-%m-%d") + fast_forward
        self.google_repeat_str = re.sub("\D", "", str(g_end_time.isoformat()))  # 202001091735000500

    def create_ical_event(self):
        event = icalendar.Event()
        event.add('summary', u'{}'.format(self.name))
        event.add('location', self.room)
        event.add('dtstart', self.start_time)
        event.add('dtend', self.end_time)
        event.add('description', self.description)
        event.add('rrule', self.repeat_rule)
        return event

    def create_google_event(self):
        service = get_calendar_service()
        iana_timezone = 'America/Montreal'

        # print("start_time: " + str(self.start_time))
        # print("start_time.isoformat: " + str(self.start_time.isoformat())[:-6])
        # print("end_time: " + str(self.end_time))
        # print("RRULE:FREQ=WEEKLY;UNTIL=" + self.google_repeat_str)

        service.events().insert(calendarId='primary',
                                body={
                                    'summary': u'{}'.format(self.name),
                                    'description': self.description,
                                    'location': self.room,
                                    'start': {'dateTime': str(self.start_time.isoformat())[:-6],
                                              'timeZone': iana_timezone},
                                    'end': {'dateTime': str(self.end_time.isoformat())[:-6], 'timeZone': iana_timezone},
                                    "recurrence": [
                                        "RRULE:FREQ=WEEKLY;UNTIL=" + self.google_repeat_str[
                                                                     :8] + "T" + self.google_repeat_str[8:] + "Z", ]
                                    # RRULE:FREQ=WEEKLY;UNTIL=20191203000000
                                }
                                ).execute()

    def __str__(self):
        """Allows for ease of reading (debugging) of the object"""
        return 'Name: ' + self.name + \
               '\nDescription: ' + self.description + \
               '\nComponent: ' + self.component + \
               '\nTimes ' + self.times + \
               '\nLocation: ' + self.room + \
               '\nRepeat Rule: ' + str(self.repeat_rule)
