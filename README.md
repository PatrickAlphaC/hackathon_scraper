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

Have fun!

### TODO
1. Github organizations not accounted for
2. Gitlab not accounted for
3. Integration with other hackathon platforms (Devfolio, Gitcoin)
4. More analytics metrics should be outputted