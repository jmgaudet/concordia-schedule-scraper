# concordia-schedule-scraper
## Summary:
Using Python and selenium, this program takes a myConcordia login, navigates through the user's class schedule, scrapes the info, and creates a .ics file.
This file can then be executed to directly populate Calendar (on Mac) with the user's entire class schedule.

The program can also export the class schedule to __Google Calendar__. 
To export to Google Cal, simply add "google" to the terminal command (see examples below).
Should you not wish to add to Google cal, simply do not add the word 'google' to the terminal command.

## Requirements:
* Python 3.7
* selenium
* Safari, Chrome, or Firefox web browser

## Directions:
1. For adding to Google Calendar, visit [this developer page](https://developers.google.com/calendar/quickstart/python) and click "Enable the Google Calendar API".
The resulting `credentials.json` file should be then added to the current directory (where these `.py` files are located)
2. The `passport.json` file must be edited to your personal username and password. Keep the quotation marks.
3. To install selenium, in terminal, type: `$ pip install selenium` __or__ `$ pip3 install selenium`
4. If using Firefox, you'll need to download __geckodriver__. This can most easily done by typing `$ brew install geckodriver` inside of terminal.
If you don't have brew, I suggest you [get brew](https://brew.sh).
5. For Chrome usage, you'll need __chromedriver__. It can also be installed by typing `$ brew install chromedriver`, and following any necessary subsequent actions.
6. In terminal, nagivate inside the folder "concordia-schedule-scraper", and type: `$ python3 main.py _______`, where you indicate your choice of browser.

##Examples:

`python3 main.py chrome`

`python3 main.py safari google`

Afterwards, a .ics will have been created in the same folder. Simply double-click it and choose which calendar to add the schedule to on iCal.