# github_report.py
import os
from bs4 import BeautifulSoup
import click
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from send_email import send_email
import json
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait

PASSWORD = os.getenv("GITHUB_LINK_PASSWORD")
EMAIL = os.getenv("GITHUB_LINK_EMAIL")

@click.command(help='Sends email to the desired contacts')
@click.option('--keywords', required=True, help='A comma separated list of keywords you want to look for')
@click.option('--days-back', default=7, help='How many days back you want to look')
@click.option('--send-mail-to', help='comma separated list of who to email')
@click.pass_context
def github_report(ctx, keywords, days_back, send_mail_to):
    keywords = keywords.split(",")
    github_projects_with_updates_map = {}
    for keyword in keywords:
        print(keyword)
        driver = github_login()
        driver = get_list_of_projects(driver, keyword)
        html = driver.page_source
        github_projects_with_updates = []
        github_projects_with_updates = find_projects_with_updates(html, days_back, github_projects_with_updates, driver)
        github_projects_with_updates_map[keyword] = github_projects_with_updates
        driver.quit()
    print(github_projects_with_updates_map)
    if send_mail_to:
        send_email(to_contacts=send_mail_to, msg_content=json.dumps(
            github_projects_with_updates_map), subject='Github Oracle Report')
                             
        

def github_login():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get("https://github.com/login")
    driver.find_element_by_id('login_field').send_keys(EMAIL)
    # driver.find_element_by_xpath('//*[@id="identifierNext"]').click()
    driver.find_element_by_id("password").send_keys(PASSWORD)
    driver.find_element_by_xpath(
        '/html/body/div[3]/main/div/form/div[4]/input[9]').click()
    time.sleep(4)
    return driver

def get_list_of_projects(driver, keyword):
    time.sleep(1)
    search_bar = driver.find_element_by_xpath(
        '/html/body/div[1]/header/div[3]/div/div/form/label/input[1]')
    search_bar.send_keys(Keys.CONTROL, 'a')
    search_bar.send_keys(Keys.BACKSPACE)
    if keyword == 'chainlink':
        search_bar.send_keys(keyword + " NOT fence" + Keys.RETURN)
    else:
        search_bar.send_keys(keyword + Keys.RETURN)
    time.sleep(4)
    driver.find_element_by_xpath(
        '/html/body/div[4]/main/div/div[2]/nav[1]/a[2]').click()
    time.sleep(1)
    try:
        driver.find_element_by_xpath(
            '/html/body/div[4]/main/div/div[3]/div/div[1]/details/summary').click()
    except:
        pass
    time.sleep(1)
    try:
        driver.find_element_by_xpath(
            '/html/body/div[4]/main/div/div[3]/div/div[1]/details/details-menu/div[2]/a[2]').click()
    except:
        pass
    time.sleep(3)
    return driver

def find_projects_with_updates(html, days_back, github_projects_with_updates, driver):
    projects_soup = BeautifulSoup(html, 'lxml')
    projects = projects_soup.find(
        'div', attrs={'class': 'code-list'})
    found_old_project = False
    for project in projects:
            relative_time_html_or_minus_one = project.find('relative-time')
            if relative_time_html_or_minus_one != -1:
                if(within_days_back(relative_time_html_or_minus_one['datetime'], days_back)):
                    github_project_url = "https://github.com" + \
                        project.find('a', attrs={'class': 'link-gray'})['href']
                    if github_project_url not in github_projects_with_updates:
                        github_projects_with_updates.append(
                            "https://github.com" + project.find('a', attrs={'class': 'link-gray'})['href'])
                else:
                    found_old_project = True
    if projects_soup.find('span', attrs={'class': "next_page disabled"}) or found_old_project:
        return github_projects_with_updates
    else:
        return find_projects_with_updates(get_next_page(html, driver), days_back, github_projects_with_updates, driver)
        

def within_days_back(relative_time_html, days_back):
    time_back = datetime.strptime(relative_time_html, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.now()
    if now > time_back + timedelta(days=days_back):
        return False
    return True

def get_next_page(html, driver):
    driver.find_element_by_class_name(
        'next_page').click()
    time.sleep(4)
    return driver.page_source
    


if __name__ == '__main__':
    github_report()
