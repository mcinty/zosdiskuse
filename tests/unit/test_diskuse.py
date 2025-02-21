from zosdiskuse.usage import FileSystemAnalyzer
import pytest


@pytest.fixture
def analyzer():
    return FileSystemAnalyzer("tests/test_data/")


def test_file_size(analyzer):
    assert analyzer.get_file_size('tests/test_data/file1.txt') != 0


def test_print_top_consumers(analyzer):
    analyzer.print_top_consumers()
    assert True
