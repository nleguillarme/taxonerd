import pytest
from click.testing import CliRunner
from taxonerd import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli, ["ask", "--help"])
    assert result.exit_code == 0
    assert not result.exception


def test_cli_with_string(runner):
    query = """
        Brown bears (Ursus arctos), which are widely distributed
        throughout the northern hemisphere, are recognised as
        opportunistic omnivores
    """
    result = runner.invoke(cli, ["ask", query])
    assert result.exit_code == 0
    assert not result.exception
