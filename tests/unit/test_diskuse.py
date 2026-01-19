"""Unit tests for disk usage analyzer."""

import pytest
from pathlib import Path
from zosdiskuse.usage import FileSystemAnalyzer


@pytest.fixture
def analyzer():
    """Create a FileSystemAnalyzer for test data."""
    return FileSystemAnalyzer("tests/test_data/")


def test_file_size(analyzer):
    """Test that file sizes are correctly retrieved."""
    size = analyzer.get_file_size('tests/test_data/file1.txt')
    assert size > 0, "File size should be greater than 0"
    assert isinstance(size, int), "File size should be an integer"


def test_file_size_nonexistent(analyzer):
    """Test that nonexistent files return 0."""
    size = analyzer.get_file_size('tests/test_data/nonexistent.txt')
    assert size == 0, "Nonexistent file should return size 0"


def test_total_size(analyzer):
    """Test that total size is calculated correctly."""
    total = analyzer.get_total_size()
    assert total > 0, "Total size should be greater than 0"
    assert isinstance(total, int), "Total size should be an integer"

    # Total should equal sum of all file sizes
    expected_total = sum(analyzer.file_sizes.values())
    assert total == expected_total, "Total size should match sum of all files"


def test_file_count(analyzer):
    """Test that file count is correct."""
    assert analyzer.file_count == 3, "Should find exactly 3 test files"


def test_dir_count(analyzer):
    """Test that directory count is correct."""
    assert analyzer.dir_count >= 1, "Should find at least 1 directory"


def test_print_top_consumers(analyzer, capsys):
    """Test that top consumers are printed without errors."""
    analyzer.print_top_consumers(num_top=2)
    captured = capsys.readouterr()
    assert len(captured.out) > 0, "Should print output"
    assert "MB" in captured.out, "Output should contain MB units"


def test_get_summary(analyzer):
    """Test that summary report is generated correctly."""
    summary = analyzer.get_summary()
    assert "Summary Report" in summary, "Summary should contain title"
    assert "Total Files: 3" in summary, "Summary should show correct file count"
    assert "MB" in summary, "Summary should contain size in MB"


def test_analyzer_with_pathlib():
    """Test that analyzer works with pathlib.Path objects."""
    path = Path("tests/test_data/")
    analyzer = FileSystemAnalyzer(path)
    assert analyzer.file_count == 3, "Should work with Path objects"


def test_nonexistent_directory():
    """Test that nonexistent directory raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Directory does not exist"):
        FileSystemAnalyzer("/nonexistent/path/that/does/not/exist")


def test_file_instead_of_directory():
    """Test that passing a file instead of directory raises NotADirectoryError."""
    with pytest.raises(NotADirectoryError, match="Path is not a directory"):
        FileSystemAnalyzer("tests/test_data/file1.txt")


def test_relative_nonexistent_path():
    """Test that relative nonexistent path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Directory does not exist"):
        FileSystemAnalyzer("./this_directory_definitely_does_not_exist_12345")


def test_lazy_mode():
    """Test that lazy mode doesn't scan immediately."""
    analyzer = FileSystemAnalyzer("tests/test_data/", lazy=True)
    assert analyzer.file_count == 0, "Lazy mode should not scan immediately"
    assert analyzer.total_size == 0, "Lazy mode should not calculate size immediately"
    assert len(analyzer.file_sizes) == 0, "Lazy mode should not load files immediately"


def test_iter_files():
    """Test streaming file iteration."""
    analyzer = FileSystemAnalyzer("tests/test_data/", lazy=True)
    files = list(analyzer.iter_files())

    assert len(files) == 3, "Should find 3 files via streaming"
    for file_path, size in files:
        assert isinstance(file_path, Path), "Should return Path objects"
        assert isinstance(size, int), "Size should be integer"
        assert size > 0, "Size should be positive"


def test_iter_files_by_size_top_n():
    """Test getting top N files by size."""
    analyzer = FileSystemAnalyzer("tests/test_data/", lazy=True)
    top_2 = list(analyzer.iter_files_by_size(top_n=2))

    assert len(top_2) == 2, "Should return exactly 2 files"
    # Verify they're sorted by size (largest first)
    assert top_2[0][1] >= top_2[1][1], "Should be sorted by size descending"


def test_iter_files_by_size_all():
    """Test getting all files sorted by size."""
    analyzer = FileSystemAnalyzer("tests/test_data/", lazy=True)
    all_files = list(analyzer.iter_files_by_size(top_n=None))

    assert len(all_files) == 3, "Should return all 3 files"
    # Verify sorted descending
    for i in range(len(all_files) - 1):
        assert all_files[i][1] >= all_files[i+1][1], "Should be sorted descending"


def test_print_top_consumers_lazy(capsys):
    """Test that print_top_consumers works in lazy mode."""
    analyzer = FileSystemAnalyzer("tests/test_data/", lazy=True)
    analyzer.print_top_consumers(num_top=2)

    captured = capsys.readouterr()
    assert len(captured.out) > 0, "Should print output"
    assert "MB" in captured.out, "Output should contain MB units"

