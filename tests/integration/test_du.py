"""Integration tests for disk usage analyzer."""

import pytest
from zosdiskuse.usage import FileSystemAnalyzer


@pytest.fixture
def analyzer():
    """Create a FileSystemAnalyzer for test data."""
    return FileSystemAnalyzer("tests/test_data/")


def test_file_sizes(analyzer):
    """Test that all test files have non-zero sizes."""
    file1_size = analyzer.get_file_size('tests/test_data/file1.txt')
    file2_size = analyzer.get_file_size('tests/test_data/file2.txt')
    file3_size = analyzer.get_file_size('tests/test_data/file3.txt')

    assert file1_size > 0, "file1.txt should have non-zero size"
    assert file2_size > 0, "file2.txt should have non-zero size"
    assert file3_size > 0, "file3.txt should have non-zero size"


def test_total_size(analyzer):
    """Test that total size matches sum of individual files."""
    total = analyzer.get_total_size()

    file1_size = analyzer.get_file_size('tests/test_data/file1.txt')
    file2_size = analyzer.get_file_size('tests/test_data/file2.txt')
    file3_size = analyzer.get_file_size('tests/test_data/file3.txt')

    expected_total = file1_size + file2_size + file3_size
    assert total == expected_total, "Total should equal sum of all files"


def test_summary(analyzer):
    """Test that summary contains expected information."""
    summary = analyzer.get_summary()

    assert isinstance(summary, str), "Summary should be a string"
    assert len(summary) > 0, "Summary should not be empty"
    assert "Total Files" in summary, "Summary should contain file count"
    assert "Total Directories" in summary, "Summary should contain directory count"
    assert "Total Size" in summary, "Summary should contain total size"

    # Verify the numbers are correct
    assert "Total Files: 3" in summary, "Should report 3 files"


def test_file_sizes_dict(analyzer):
    """Test that file_sizes dictionary is populated correctly."""
    assert len(analyzer.file_sizes) == 3, "Should have 3 files in dictionary"

    # All values should be positive integers
    for file_path, size in analyzer.file_sizes.items():
        assert isinstance(size, int), f"Size for {file_path} should be int"
        assert size > 0, f"Size for {file_path} should be positive"


def test_counts(analyzer):
    """Test that file and directory counts are correct."""
    assert analyzer.file_count == 3, "Should count exactly 3 files"
    assert analyzer.dir_count >= 1, "Should count at least 1 directory"
    assert isinstance(analyzer.file_count, int), "File count should be int"
    assert isinstance(analyzer.dir_count, int), "Directory count should be int"

