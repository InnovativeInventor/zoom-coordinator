from icalendar import Calendar, Event
from app import check_teacher
from schedule import block_iter, ScheduleManager
import pytz
import datetime

from utils import *

CLASSDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def make_calendar(email, firstname, lastname):
    """
    Returns an ical of the user's schedule
    """
    # ScheduleManager().createSchedule(email, firstname, lastname, check_teacher(email))
    user_schedule = ScheduleManager().getSchedule(email, firstname, lastname, check_teacher(email))
    user_schedule.init_db_connection()
    user_schedule.fetch_schedule()
    
    today_offset = datetime.date.today().weekday() 
    this_monday = datetime.date.today() - datetime.timedelta(days=today_offset)

    # Taken from documentation
    cal = Calendar()
    cal['summary'] = 'Choate Zoom Coordinator Schedule'
    for count, each_day in enumerate(CLASSDAYS):
        for block, start_time in block_iter(email, firstname, lastname, isTeacher=check_teacher(email), datetime_needed=True, weekday=each_day):
            start_time = start_time.replace(year=this_monday.year, month=this_monday.month, day=this_monday.day) + datetime.timedelta(days=count)
            
            block_data = user_schedule.schedule[block]
            if block_data:
                event = Event()
                # event['summary'] = block + ' block class'
                event['LOCATION'] = "https://zoom.us/j/" + str(block_data.get('meeting_id'))
                event['summary'] = block_data.get('course_name').title()
                event['DESCRIPTION'] = "Zoom link: https://zoom.us/j/" + str(block_data.get('meeting_id')) + "\nMeeting ID: " + str(block_data.get('meeting_id'))
                event.add('rrule', {'freq': 'weekly', 'count': 10})

                event.add('dtstart', start_time)
                event.add('dtend', start_time + datetime.timedelta(minutes=50))

                cal.add_component(event)
    user_schedule.end_db_connection()
    return cal

