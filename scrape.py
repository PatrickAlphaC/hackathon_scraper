import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import csv
import json
import click
import logging as log

class Hackathon:
    def __init__(self, url, platform):
        self.url = url
        self.prizes = None
        self.platform = platform

    def __str__(self):
        return str(self.__dict__)
    
    def to_dict(self):
        return self.__dict__

# Get blockchain hackathons
log.basicConfig(level=log.INFO)

# Sample command run:
# python scrape.py --hackathon-keyword blockchain
@click.command(help='Gets github information about hackathon from hackathon platforms')
@click.option('--hackathon-keyword', required=True, help='What kind of hackathons are you searching for')
@click.option('--next-week-file', default="next_week.json", help='Where to store results of the scrape')
def scrape_hackathons(hackathon_keyword, next_week_file):
    hackathons = []
    devpost_hackathons = get_devpost_hackathons(hackathon_keyword)
    #TODO Devfolio, Gitcoin
    hackathons.extend(devpost_hackathons)
    with open(next_week_file, "w") as outfile:
        json.dump([hackathon.to_dict() for hackathon in hackathons], outfile)

def get_devpost_hackathons(hackathon_keyword):
    hackathons = []
    result = requests.get(
        "https://devpost.com/hackathons?utf8=%E2%9C%93&search={}&challenge_type=all&sort_by=Submission+Deadline".format(hackathon_keyword))
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    featured_challenges = soup.find_all(
        'a', attrs={'data-role': 'featured_challenge'})
    for featured_challenge in featured_challenges:
        hackathon = Hackathon(featured_challenge.attrs['href'], 'devpost')
        time_left = None
        try:
            time_left = featured_challenge.find(
                "time", attrs={"class": "value timeago"}).text
        except:
            continue
        time_left = datetime.strptime(
            time_left[:-4], "%b %d, %Y %I:%M %p")
        now = datetime.now()
        if now > time_left - timedelta(days=7):
            hackathons.append(hackathon)
            log.info("Added Hackathon with URL:{}".format(hackathon.url))
            prize_value = featured_challenge.find(
                "span", attrs={"data-currency-value": ""})
            hackathon.prizes = int(prize_value.text.replace(
                "$", "").replace(",", "").replace("€", ""))
    return hackathons

def main():
    scrape_hackathons()


if __name__ == '__main__':
    main()
