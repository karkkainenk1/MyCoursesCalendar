# MyCoursesCalendar
This application improves the ics file given by MyCourses by making the event name more descriptive (e.g. "T-61.3050 L1, T1 (Machine Learning: Basic Principles)"). The output file can be imported to Google Calendar for example.

## Requirements
This script requires BeautifulSoup and iCalendar Python packages, so you should run the following commands to install them before usage:
<pre>
pip install beautifulsoup4
pip install icalendar
</pre>

## Usage
First, get your personal calendar URL from https://mycourses.aalto.fi/calendar/export.php by choosing a suitable time period and clicking the "Get subscription URL" button. Then, go to the same folder with this script and execute the following command:
<pre>python tunkki.py --url "your-url-here"</pre>

By default, this script will ignore the exercise sessions. The reason for this is that the original calendar includes all the possible sessions instead of just the ones that you have signed up for, so your calendar will get filled with unwanted events. If you really want to include the exercise sessions also, just add the parameter --include-exercise-sessions after the command.

The output file will be output.ics by default, and it can be changed with the parameter --output anotherfile.ics .
