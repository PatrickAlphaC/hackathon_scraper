from click.testing import CliRunner
from hackathon_scraper import github_follow_up
import pytest
import time
from flaky import flaky

# def test_github_follow_up_one_repo():
#     runner = CliRunner()
#     result = runner.invoke(github_follow_up.github_follow_up, ["--github-keyword",
#                                                                "HealthInsurance", "--input-file", "test_data.json", "--output-file", "test-output.txt"])
#     assert 'Number of devpost hackathon projects 1' in result.output


def test_github_follow_up_two_repos_and_org():
    runner = CliRunner()
    result = runner.invoke(github_follow_up.github_follow_up, ["--github-keyword",
                                                               "const", "--input-file", "test_data.json", "--output-file", "test2-output.txt"])
    assert 'Number of devpost hackathon projects 2' in result.output


@flaky
def test_get_hackathons_with_keyword():
    hackathons = github_follow_up.read_from_file("test_data.json")
    keyworded_hackathons = github_follow_up.get_hackathons_with_keyword(
        hackathons, "healthinsurance")
    assert len(keyworded_hackathons[0]) == 1


def test_is_organization():
    non_org_url = "https://github.com/AlphaVHacks/BlockTradeApp/"
    org_url = "https://github.com/AlphaVHacks/"
    assert github_follow_up.is_organization(non_org_url) == False
    assert github_follow_up.is_organization(org_url) == True


def test_get_org_name():
    org_url = "https://github.com/AlphaVHacks/"
    assert github_follow_up.get_org_name(org_url) == "AlphaVHacks"


@flaky
def test_repo_has_keyword():
    repo_url = "https://github.com/PatrickAlphaVantage/hackathon_scraper/"
    keyword = "scrape"
    assert github_follow_up.repo_has_keyword(repo_url, keyword) == True


def test_get_gitcoin_hackathons():
    github_follow_up.get_gitcoin_hackathons("test")
    assert False
