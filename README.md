# concordia-schedule-scraper
### Abstract:
Using Python and Selenium, this program takes a myConcordia login, navigates through the user's class schedule, scrapes the info, and creates a .ics file.
This file can then be executed to directly populate Calendar (on Mac) with the user's entire class schedule.

### Requirements:
* Python 3.7
* selenium
* Safari web browser (since this is primarily for iCal, Safari should be installed already)

### Directions:
1. For adding to Google Calendar, visit [this developer page](https://developers.google.com/calendar/quickstart/python) and click "Enable the Google Calendar API".
The resulting `credentials.json` file should be then added to the current directory (where these `.py` files are located)
2. The `passport.json` file must be edited to your personal username and password. Keep the quotation marks.
3. To install selenium, in terminal, type: `$ pip install selenium` __or__ `$ pip3 install selenium`
4. In terminal, nagivate inside the folder "concordia-schedule-scraper", and type: `$ python3 main.py`

Afterwards, a .ics will have been created in the same folder. Simply double-click it and choose which calendar to add the schedule to on iCal.
If some error message appeared, perhaps Google cal was not configured properly/completely. The line `produce_google_cal()` inside of `__main__` can be commented out to skip adding the info to Google calendar.
