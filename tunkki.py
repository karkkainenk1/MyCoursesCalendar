import sys
import argparse

from bs4 import BeautifulSoup
from icalendar import Calendar

if sys.version_info > (3, 0, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen
    from urllib2 import URLError

ignore_problem_sessions = True
course_names = {}


def open_url(url):
    if sys.version_info > (3, 0, 0):
        with urlopen(url) as remote_calendar:
            if remote_calendar.status != 200:
                raise AttributeError("Invalid URL! Server responded: {0!s} ({1!s})".format(remote_calendar.status,
                                                                                           remote_calendar.msg))
            data = remote_calendar.readall()
    else:
        try:
            remote_calendar = urlopen(url)
            if remote_calendar.code != 200:
                raise AttributeError("Invalid URL! Server responded: {0!s} ({1!s})".format(remote_calendar.code,
                                                                                           remote_calendar.msg))
            data = remote_calendar.read()
        except URLError as e:
            raise AttributeError("URL Resulted in URLError: {0!s}".format(e))
        finally:
            remote_calendar.close()

    return data


def main(url, output):
    cal_text = open_url(url)

    cal_input = Calendar.from_ical(cal_text, True)
    cal_output = Calendar()

    for event in cal_input[0].walk('vevent'):
        event_type = parse_event_type(event)
        if should_ignore_event_type(event_type):
            continue

        course_code = parse_course_code(event)
        event_room = parse_event_room(event)
        course_name = get_course_name(course_code)

        event['summary'] = generate_event_description(course_code, event_type, event_room, course_name)
        cal_output.add_component(event)

    with open(output, 'wb') as output_calendar:
        output_calendar.write(cal_output.to_ical())


def generate_event_description(course_code, event_type, event_room, course_name):
    description = course_code + " " + event_type
    if len(event_room) > 0:
        description += ", " + event_room
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
    if ', ' in orig_summary:
        event_room = orig_summary.split(", ")[1].split(" ")[0]
    return event_room


def get_course_name(course_code):
    course_name = ""
    if course_code in course_names:
        course_name = course_names.get(course_code)
    else:
        search_page = urlopen('https://mycourses.aalto.fi/course/search.php?search=' + course_code).read()
        soup = BeautifulSoup(search_page, "html.parser")
        course_name = soup.find('span', {'class': 'coursename'}).text.split(" - ")[1].split(", ")[0]
        course_names[course_code] = course_name

    return course_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", "-U", help="MyCourses Calendar URL", required=True)
    parser.add_argument("output_file", help="Output iCal calendar file")
    args = parser.parse_args()
    main(args.url, args.output_file)
