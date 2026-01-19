# z/OS Disk Usage

A simple Python package that provides disk usage analysis by finding the largest files under a given path.

## Features

- Analyze disk usage for any directory
- Find top space-consuming files
- Generate summary reports
- Fast and efficient file system traversal
- Graceful error handling for inaccessible files

## Requirements

- Python 3.9 or higher

## Installation

### From Source

```bash
git clone https://github.com/mcinty/zosdiskuse.git
cd zosdiskuse
python3 -m pip install .
```

### Development Installation

```bash
git clone https://github.com/mcinty/zosdiskuse.git
cd zosdiskuse
python3 -m pip install -e ".[dev]"
```

## Usage

### Command Line

After installation, you can use the `zosdiskuse` command:

```bash
zosdiskuse /path/to/directory
```

Or run as a module:

```bash
python3 -m zosdiskuse.usage /path/to/directory
```

### As a Library

#### Standard Usage (Eager Loading)

```python
from zosdiskuse import FileSystemAnalyzer

# Analyze a directory (loads all files into memory)
analyzer = FileSystemAnalyzer("/path/to/directory")

# Get summary report
print(analyzer.get_summary())

# Get total size
total_bytes = analyzer.get_total_size()
print(f"Total: {total_bytes / (1024**3):.2f} GB")

# Show top 10 largest files
analyzer.print_top_consumers(num_top=10)

# Get size of a specific file
size = analyzer.get_file_size("/path/to/directory/file.txt")
print(f"File size: {size / (1024**2):.2f} MB")
```

#### Memory-Efficient Usage (Lazy/Streaming)

For large filesystems with millions of files, use lazy mode to avoid loading everything into memory:

```python
from zosdiskuse import FileSystemAnalyzer

# Create analyzer in lazy mode (doesn't scan immediately)
analyzer = FileSystemAnalyzer("/large/filesystem", lazy=True)

# Stream through all files (memory efficient)
for file_path, size in analyzer.iter_files():
    if size > 1024**3:  # Files larger than 1GB
        print(f"Large file: {file_path}")

# Get top 10 largest files without loading everything
for file_path, size in analyzer.iter_files_by_size(top_n=10):
    print(f"{file_path}: {size / (1024**3):.2f} GB")

# Print top consumers (works in both modes)
analyzer.print_top_consumers(num_top=20)
```

#### Advanced: Custom Processing

```python
from zosdiskuse import FileSystemAnalyzer

analyzer = FileSystemAnalyzer("/path", lazy=True)

# Find all Python files larger than 100KB
large_python_files = [
    (path, size)
    for path, size in analyzer.iter_files()
    if path.suffix == '.py' and size > 100 * 1024
]

# Calculate total size of log files
log_size = sum(
    size
    for path, size in analyzer.iter_files()
    if path.suffix == '.log'
)
print(f"Total log files: {log_size / (1024**2):.2f} MB")
```

## Example Output

```
Summary Report:
----------------
Total Files: 1523
Total Directories: 87
Total Size: 2847.32 MB

Total size: 2847.32 MB

1. /path/to/large_file1.bin: 450.23 MB
2. /path/to/large_file2.log: 389.45 MB
3. /path/to/large_file3.dat: 234.67 MB
...
```

## Development

### Setup Development Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

This project uses modern Python tooling:

```bash
# Format and lint with ruff
ruff check .
ruff format .

# Type checking with mypy
mypy src/
```

### Building

```bash
python3 -m build
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Project Links

- **Homepage**: https://github.com/mcinty/zosdiskuse
- **Issues**: https://github.com/mcinty/zosdiskuse/issues

## Changelog

### Version 0.0.1 (2026-01-19)

- Initial release
- Basic disk usage analysis functionality
- Command-line interface
- Python 3.9+ support with modern type hints
- Pathlib-based file operations
- Comprehensive error handling
