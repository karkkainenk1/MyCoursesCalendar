from icalendar import Calendar, Event
from bs4 import BeautifulSoup
from sets import Set
import urllib2

##### CONFIG #####
calendar_url = 'https://mycourses.aalto.fi/calendar/export_execute.php?preset_what=all&preset_time=recentupcoming&userid=<userid>&authtoken=<authtoken>'
ignore_problem_sessions = True
output_file_name = 'output.ics'
##################


def main():
    cal_text = urllib2.urlopen(calendar_url).read()
    cal_input = Calendar.from_ical(cal_text, True)
    cal_output = Calendar()
    
    for event in cal_input[0].walk('vevent'):
        event_type = parse_event_type(event)
        if should_ignore_event_type(event_type): continue
    
        course_code = parse_course_code(event)
        event_room = parse_event_room(event)
        course_name = get_course_name(course_code)
    
        event['summary'] = generate_event_description(course_code, event_type, event_room, course_name)
        cal_output.add_component(event)
    
    output_file = open(output_file_name, 'w')
    output_file.write(cal_output.to_ical())

def generate_event_description(course_code, event_type, event_room, course_name):
    description = course_code + " " + event_type
    if len(event_room) > 0: description += ", " + event_room
    description += " (" + course_name + ")"
    return description

def should_ignore_event_type(event_type):
    return ignore_problem_sessions and event_type[0] == 'H'

def parse_course_code(event):
    orig_category = event.get('categories')
    course_code = orig_category.split('_')[0]
    return course_code

def parse_event_type(event):
    orig_summary = event.get('summary')
    event_type = orig_summary.split(' ')[0]
    return event_type

def parse_event_room(event):
    orig_summary = event.get('summary')
    event_room = ""
    if ', ' in orig_summary: event_room = orig_summary.split(", ")[1].split(" ")[0]
    return event_room

course_names = {}
def get_course_name(course_code):
    course_name = ""
    if course_names.has_key(course_code): 
        course_name = course_names.get(course_code)
    else:
        search_page = urllib2.urlopen('https://mycourses.aalto.fi/course/search.php?search=' + course_code).read()
        soup = BeautifulSoup(search_page, "html.parser")
        course_name = soup.find('span',{'class':'coursename'}).text.split(" - ")[1].split(", ")[0]
        course_names[course_code] = course_name
        
    return course_name


if __name__ == "__main__": main()
