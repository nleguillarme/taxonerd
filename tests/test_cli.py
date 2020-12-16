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
    print(result.output.strip())
    assert result.exit_code == 0
    assert not result.exception


# def test_cli_with_option(runner):
#     result = runner.invoke(cli.main, ['--as-cowboy'])
#     assert not result.exception
#     assert result.exit_code == 0
#     assert result.output.strip() == 'Howdy, world.'
#
#
# def test_cli_with_arg(runner):
#     result = runner.invoke(cli.main, ['Nicolas'])
#     assert result.exit_code == 0
#     assert not result.exception
#     assert result.output.strip() == 'Hello, Nicolas.'
