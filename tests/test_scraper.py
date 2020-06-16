from click.testing import CliRunner
from hackathon_scraper import github_follow_up
import pytest


# def test_correct():
#     assert github_follow_up.github_follow_up("express", "test_data.json") == 1


def test_github_follow_up():
    runner = CliRunner()
    result = runner.invoke(github_follow_up.github_follow_up, ["--github-keyword",
                                                               "HealthInsurance", "--read-from-file", "test_data.json"])
    assert 'Number of hackathon projects 1' in result.output
