import json
import requests
from bs4 import BeautifulSoup
import click

import logging as log
log.basicConfig(level=log.INFO)

# Sample run
# python github_follow_up.py --github-keyword chainlink
@click.command(help='Gets github information about hackathon from hackathon platforms')
@click.option('--github-keyword', required=True, help='What project youre looking for in github')
@click.option('--read-from-file', default='next_week.json', help='What projects to check out')
def github_follow_up(github_keyword, read_from_file):
    # Opening JSON file
    file = open(read_from_file)
    hackathons = json.load(file)
    number_of_keyworded_hackathons = 0
    hackathons_with_keyword = []

    for hackathon in hackathons:
        result = requests.get(hackathon['url'].split(
            "devpost.com")[0] + "devpost.com/submissions")
        src = result.content
        soup = BeautifulSoup(src, 'lxml')
        submissions = soup.find_all(
            'a', attrs={'class': 'block-wrapper-link fade link-to-software'})
        for submission in submissions:
            submission_page = requests.get(submission.attrs['href'])
            submission_src = submission_page.content
            submission_soup = BeautifulSoup(submission_src, 'lxml')
            possible_githubs = submission_soup.find_all('a')
            for possible_github in possible_githubs:
                if 'href' in possible_github.attrs and "github" in possible_github.attrs['href']:
                    search_suffix = "/search?q={}&unscoped_q={}".format(
                        github_keyword, github_keyword)
                    log.info(possible_github.attrs['href'] + search_suffix)
                    github_result = requests.get(
                        possible_github.attrs['href'] + search_suffix)
                    github_src = github_result.content
                    github_soup = BeautifulSoup(github_src, 'lxml')
                    h3_tags = github_soup.find_all('h3')
                    for h3_tag in h3_tags:
                        if "code result" in h3_tag.text:
                            number_of_keyworded_hackathons += 1
                            hackathons_with_keyword.append(hackathon)

    total_prize_pool = 0
    for hackathon in hackathons_with_keyword:
        total_prize_pool += hackathon['prizes']

    if number_of_keyworded_hackathons > 0:
        click.echo(" Number of hackathon projects {}".format(
            number_of_keyworded_hackathons))
        log.info(" Average prize pool of submissions: " +
                 str(total_prize_pool / number_of_keyworded_hackathons))
    else:
        log.info(" No hackathons had that keyword :(")
    # Closing file
    file.close()
    return number_of_keyworded_hackathons


def main():
    github_follow_up()


if __name__ == '__main__':
    main()
