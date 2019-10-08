import json
import time
from sys import argv

import icalendar
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from course_event import ScheduledCourse

courses = []
sleep_scale = 5  # MUST BE 3 OR GREATER. '5' is the recommended average amount of time needed to wait

try:
    if len(argv) > 1:
        b = argv[1].lower()
    else:
        b = 'Null_Argument'

    if b == 'safari':
        browser = webdriver.Safari()
    elif b == 'firefox':
        browser = webdriver.Firefox()
    elif b == 'chrome':
        browser = webdriver.Chrome()
    else:
        raise ValueError(
            'ERROR: Bad argument.\nShould have typed either \"chrome\", \"safari\", or \"firefox\" as an argument here:\n'
            '\"$ python3 main.py ______\"\nTry again.')
except ValueError as err:
    print(err.args[0])
    exit(0)


def login():
    """Using the info from the json file, opens the Safari browser and begins navigation"""
    with open('passport.json', 'r') as read_file:
        data = json.load(read_file)
    browser.get('https://my.concordia.ca/psp/upprpr9/?cmd=login&languageCd=ENG&')
    # browser.maximize_window()
    browser.find_element_by_id('userid').send_keys(data['username'])
    browser.find_element_by_id('pwd').send_keys(data['password'])
    browser.find_element_by_class_name('form_button_submit').click()


def get_term_info(term):
    """For each term, hides the dropped courses, then grabs each courses' info.
    Returns a large list containing multiple dictionaries, where each describes a single course."""
    term.find_elements_by_tag_name('td')[0].find_element_by_tag_name('input').click()
    browser.find_element_by_id('DERIVED_SSS_SCT_SSR_PB_GO').click()
    time.sleep(sleep_scale - 1)
    try:
        browser.find_element_by_id('DERIVED_REGFRM1_SA_STUDYLIST_D').click()
        time.sleep(1)
        browser.find_element_by_id('DERIVED_REGFRM1_SA_STUDYLIST_SHOW$14$').click()
    except NoSuchElementException:
        pass
    time.sleep(sleep_scale - 2)
    _courses = browser.find_elements_by_class_name('PSGROUPBOXWBO')[1:]
    for course in _courses:
        for comp in course.find_elements_by_class_name('PSLEVEL3GRID')[1].find_elements_by_tag_name('tr')[1:]:
            c = {}
            c['name'] = course.find_element_by_class_name('PAGROUPDIVIDER').get_attribute('innerHTML')
            c['number'], c['section'], c['component'], c['times'], c['room'], c['instructor'], c['start_end'] = \
                map(lambda x: x.text.strip('\n'), comp.find_elements_by_tag_name('td'))
            courses.append(c)


def browser_collection():
    """Captures and navigates through each available semester"""
    url = 'https://campus.concordia.ca/psc/pscsprd/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL?Page=SSR_SSENRL_LIST&Action=A&TargetFrameName=None'
    browser.get(url)
    get_terms = lambda: browser.find_element_by_css_selector('.PSLEVEL2GRID').find_elements_by_tag_name('tr')[1:]
    terms = get_terms()
    num_terms = len(terms)
    for _ in range(num_terms):
        browser.get(url)
        terms = get_terms()
        get_term_info(terms[num_terms - 1])
        num_terms -= 1
    browser.close()


def create_txt_reference():
    with open('courses.txt', 'w') as text_file:
        text_file.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + '\n')
        for item in courses:
            text_file.write("%s\n" % item)


def produce_calendars():
    cal = icalendar.Calendar()
    if len(argv) > 2:   # Checking if the user wants to export the calendar details to their Google Cal
        a = argv[2].lower()
    else:
        a = 'no_google'
    # Loop thru each course in the list courses
    for course in courses:
        event = ScheduledCourse(**course)
        cal.add_component(event.create_ical_event())
        if a == 'google':
            event.create_google_event()
    with open('output.ics', 'wb') as f:
        f.write(cal.to_ical())
    print('\"output.ics\" file successfully created')


if __name__ == '__main__':
    login()
    time.sleep(sleep_scale)  # time.sleep() is necessary, since myConcordia takes a while to load
    browser_collection()
    create_txt_reference()
    produce_calendars()
