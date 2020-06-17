# Hackathon Scraper

Hi all, this repo is to help out getting OKRs for DevRel folks!

Here is how it works:

1. Every week run `python scrape.py --hackathon-keyword <KEYWORD_HERE>`
With `<KEYWORD_HERE> being the type of hackathon you're looking for

This will save a file to `next_week.json` which will have a list of hackathons that you'll look to check out once submissions are availible. 

2. After each week, run `python github_follow_up.py --github-keyword <GITHUB_KEYWORD>`

This will pull from `next_week.json` and give you the github projects from submissions that have the project you're looking for!

Example:
At the start of the week I run:
`python scrape.py --hackathon-keyword blockchain`
This will show me all the `blockchain` hackathons that are ending in 7 days or less.

Then I run:
`python github_follow_up.py --github-keyword chainlink`
This will show me all the hackathon submissions that recently ended that have their github repo have that keyword in it.

Sample output:
```
$ python github_follow_up.py --github-keyword chainlink
_________________________________
Total submissions: 53 + 45 = 98
2020-06-16 23:31:14.815999
 No projects had that keyword :(
```

```
$ python github_follow_up.py --github-keyword const --input-file tests/test_data.json 
_________________________________
Total submissions: 5 + 45 = 50
2020-06-16 23:40:15.635757
 Number of devpost hackathon projects 2
INFO:root:[{'url': 'https://alphavhack.devpost.com/', 'prizes': 165375, 'platform': 'devpost'}, {'url': 'https://alphavhack.devpost.com/', 'prizes': 165375, 'platform': 'devpost'}]
INFO:root: Average prize pool of submissions: 165375.0
 Number of gitcoin hackathon projects 3
INFO:root:['/hackathon/GitxChange/projects/', '/hackathon/GitxChange/projects/', '/hackathon/GitxChange/projects/']
INFO:root: Average prize pool of submissions: 110250.0
```
Have fun!

### Testing
Note: Due to github rate limiting you have to test each one at a time

Run run `cd tests; pytest -v` or to run a single test `cd tests; pytest -v -k test_repo_has_keyword`

### TODO
- [x] Github organizations accounted for
- [x] If a hackathon has multiple pages of submissions it only gets the first page
- [ ] Gitlab accounted for
- [ ] Devfolio Integration
- [x] Gitcoin integration
- [ ] More analytics metrics 
- [ ] Github OAuth key added so we don't get rate limited and have to run induvidual tests