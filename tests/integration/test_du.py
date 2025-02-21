import pytest

from zosdiskuse.usage import FileSystemAnalyzer


@pytest.fixture
def analyzer():
    return FileSystemAnalyzer("tests/test_data/")


def test_file_sizes(analyzer):
    assert analyzer.get_file_size('tests/test_data/file1.txt') != 0
    assert analyzer.get_file_size('tests/test_data/file2.txt') != 0
    assert analyzer.get_file_size('tests/test_data/file3.txt') != 0


def test_total_size(analyzer):
    analyzer.get_total_size()


def test_summary(analyzer):
    s = analyzer.get_summary()
    print(s)
