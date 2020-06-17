# https://towardsdatascience.com/data-science-skills-web-scraping-javascript-using-python-97a29738353f
# The link above described scraping with selenium and firefox
import json
import requests
from bs4 import BeautifulSoup
import click
from datetime import datetime, timedelta
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

import logging as log
log.basicConfig(level=log.INFO)

# Sample run
# python github_follow_up.py --github-keyword chainlink
@click.command(help='Gets github information about hackathon from hackathon platforms')
@click.option('--github-keyword', required=True, help='What project youre looking for in github')
@click.option('--input-file', default='next_week.json', help='What projects to check out')
@click.option('--output-file', default='results.txt', help='What projects to check out')
def github_follow_up(github_keyword, input_file, output_file):
    # Opening JSON file
    hackathons = read_from_file(input_file)
    keyworded_hackathon_projects, total_submissions = get_hackathons_with_keyword(
        hackathons, github_keyword)
    # Gitcoin you don't have to start from a week ago, you can just scrape the most recently finished
    gitcoin_keyworded_hackathon_projects, total_gitcoin_submissions = get_gitcoin_hackathons(
        github_keyword)
    click.echo("Total submissions: {} + {} = {}".format(total_submissions,
                                                        total_gitcoin_submissions, (total_submissions + total_gitcoin_submissions)))
    output_metrics(keyworded_hackathon_projects,
                   gitcoin_keyworded_hackathon_projects)
    output_to_file(keyworded_hackathon_projects,
                   gitcoin_keyworded_hackathon_projects, output_file)


def get_hackathons_with_keyword(hackathons, github_keyword):
    hackathons_with_keyword = []
    total_submissions = 0
    for hackathon in hackathons:
        has_submissions = True
        submission_page_number = 0
        while(has_submissions):
            submission_page_number += 1
            result = requests.get(hackathon['url'].split(
                "devpost.com")[0] + "devpost.com/submissions?page={}".format(submission_page_number))
            src = result.content
            soup = BeautifulSoup(src, 'lxml')
            submissions = soup.find_all(
                'a', attrs={'class': 'block-wrapper-link fade link-to-software'})
            if len(submissions) == 0:
                has_submissions = False
                break
            for submission in submissions:
                submission_page = requests.get(submission.attrs['href'])
                submission_src = submission_page.content
                submission_soup = BeautifulSoup(submission_src, 'lxml')
                possible_githubs = submission_soup.find_all('a')
                for possible_github in possible_githubs:
                    if 'href' in possible_github.attrs and "github" in possible_github.attrs['href']:
                        total_submissions += 1
                        if github_repo_has_keyword(possible_github.attrs['href'], github_keyword):
                            hackathons_with_keyword.append(hackathon)
    return hackathons_with_keyword, total_submissions


def github_repo_has_keyword(github_url, github_keyword):
    if is_organization(github_url):
        github_org_result = requests.get(github_url)
        github_org_src = github_org_result.content
        github_org_soup = BeautifulSoup(
            github_org_src, 'lxml')
        try:
            org_repos = github_org_soup.find(
                'div', attrs={"class": "org-repos repo-list"})
            org_repo_headers = org_repos.find_all('h3')
        except:
            return False
        for org_repo_header in org_repo_headers:
            if(repo_has_keyword(
                    "https://github.com{}".format(org_repo_header.find('a').attrs['href']), github_keyword)):
                return True
    else:
        search_url = github_url + "/search?q={}&unscoped_q={}".format(
            github_keyword, github_keyword)
        if(repo_has_keyword(search_url, github_keyword)):
            return True
    return False


def get_gitcoin_hackathons(github_keyword):
    hackathons_with_keyword = []
    total_submissions = 0
    result = requests.get("https://gitcoin.co/hackathon-list")
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    finished_hackathons = soup.find(
        text=re.compile('Finished Hackathons')).parent.parent.find_all(
        'div', attrs={"class": "card-body col-9 col-sm-8"})
    recent_finished_hackathons = get_finished_hackathons_from_last_week(
        finished_hackathons)
    for recent_finished_hackathon in recent_finished_hackathons:
        links = recent_finished_hackathon.find_all('a')
        for link in links:
            if "projects" in link.attrs['href']:
                # projects_result = requests.get(
                #     "https://gitcoin.co/{}".format(link.attrs['href']), timeout=(3.05, 27))
                options = Options()
                options.headless = True
                driver = webdriver.Firefox()
                driver.get("https://gitcoin.co/{}".format(link.attrs['href']))
                time.sleep(20)
                html = driver.page_source
                driver.quit()
                # projects_src = projects_result.content
                projects_soup = BeautifulSoup(html, 'lxml')
                github_links = projects_soup.find_all('a')
                for github_link in github_links:
                    if 'href' in github_link.attrs and 'github.com' in github_link.attrs['href']:
                        total_submissions += 1
                        if github_repo_has_keyword(github_link.attrs['href'], github_keyword):
                            hackathons_with_keyword.append(link.attrs['href'])
    return hackathons_with_keyword, total_submissions


def get_finished_hackathons_from_last_week(finished_hackathons):
    recent_finished_hackathons = []
    for finished_hackathon in finished_hackathons:
        time_set = finished_hackathon.find_all("time")
        time_end = datetime.strptime(time_set[1].text, "%m/%d/%Y")
        now = datetime.now()
        if now < time_end + timedelta(days=7):
            recent_finished_hackathons.append(finished_hackathon)
    return recent_finished_hackathons


def is_organization(possible_github_link):
    condensed_link = possible_github_link.replace("//", "/").strip()
    if condensed_link.endswith("/"):
        condensed_link = condensed_link[:-1]
    if len(condensed_link.split("/")) <= 3:
        return True
    return False


def get_org_name(possible_github_link):
    condensed_link = possible_github_link.replace("//", "/").strip()
    if condensed_link.endswith("/"):
        condensed_link = condensed_link[:-1]
    return condensed_link.split("/")[2]


def repo_has_keyword(repo_url, github_keyword):
    search_url = repo_url + "/search?q={}&unscoped_q={}".format(
        github_keyword, github_keyword)
    github_result = requests.get(search_url)
    github_src = github_result.content
    github_soup = BeautifulSoup(github_src, 'lxml')
    h3_tags = github_soup.find_all('h3')
    for h3_tag in h3_tags:
        if "code result" in h3_tag.text:
            return True
    return False


def read_from_file(input_file):
    file = open(input_file)
    hackathons = json.load(file)
    file.close()
    return hackathons


def output_to_file(keyworded_hackathons, gitcoin_keyworded_hackathons, output_file):
    file = open(output_file, "a+")
    file.write(str(datetime.now()))
    file.write(str([str(hackathon) for hackathon in keyworded_hackathons]))
    file.write(str([str(hackathon)
                    for hackathon in gitcoin_keyworded_hackathons]))
    file.close()


def output_metrics(keyworded_hackathons, gitcoin_keyworded_hackathons):
    click.echo(str(datetime.now()))
    total_prize_pool = 0
    for hackathon in keyworded_hackathons:
        total_prize_pool += hackathon['prizes']

    if len(keyworded_hackathons) > 0 and len(gitcoin_keyworded_hackathons) > 0:
        click.echo(" Number of devpost hackathon projects {}".format(
            len(keyworded_hackathons)))
        log.info(keyworded_hackathons)
        log.info(" Average prize pool of submissions: " +
                 str(total_prize_pool / len(keyworded_hackathons)))
        # gitcoin
        click.echo(" Number of gitcoin hackathon projects {}".format(
            len(gitcoin_keyworded_hackathons)))
        log.info(gitcoin_keyworded_hackathons)
        log.info(" Average prize pool of submissions: " +
                 str(total_prize_pool / len(gitcoin_keyworded_hackathons)))
    else:
        click.echo(" No projects had that keyword :(")


def main():
    github_follow_up()


if __name__ == '__main__':
    main()
