import json
import time

import icalendar
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from course_event import ScheduledCourse

courses = []
sleep_scale = 5  # '5' is the recommended average amount of time needed to wait
browser = webdriver.Safari()


def login():
    """Using the info from the json file, opens the Safari browser and begins navigation"""
    with open("passport.json", "r") as read_file:
        data = json.load(read_file)
    browser.get('https://my.concordia.ca/psp/upprpr9/?cmd=login&languageCd=ENG&')
    browser.maximize_window()
    browser.find_element_by_id('userid').send_keys(data['username'])
    browser.find_element_by_id('pwd').send_keys(data['password'])
    browser.find_element_by_class_name('form_button_submit').click()


def get_term_info(term):
    """For each term, hides the dropped courses, then grabs each courses' info.
    Returns a single large list containing multiple dictionaries, where each describes a single course."""
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
    """Captures and then navigates successively through each available term"""
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
    """Creates a txt file in order to have a clearer view of what exactly has been scraped"""
    with open('courses.txt', 'w') as text_file:
        for item in courses:
            text_file.write("%s\n" % item)


def produce_ical():
    """Using the class ScheduledCourse, this method organizes the gathered list of dictionaries,
    and writes them to an executable .ics file"""
    cal = icalendar.Calendar()
    for course in courses:
        event = ScheduledCourse(**course)
        # print(event)
        cal.add_component(event.create_ical_event())
    with open('output.ics', 'wb') as f:
        f.write(cal.to_ical())


def produce_google_cal():
    for course in courses:
        google_event = ScheduledCourse(**course)
        google_event.create_google_event()


if __name__ == '__main__':
    login()
    time.sleep(sleep_scale)  # time.sleep() is necessary, since myConcordia takes a while to load
    browser_collection()
    create_txt_reference()
    # produce_ical()
    produce_google_cal()
