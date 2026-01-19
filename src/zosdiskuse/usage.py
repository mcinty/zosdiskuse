"""File system analysis utilities for disk usage calculation."""

import heapq
import sys
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple, Union


class FileSystemAnalyzer:
    """Analyzes file system usage by walking directory trees.

    This class provides both eager (load all into memory) and lazy (streaming)
    approaches to analyzing disk usage.
    """

    def __init__(self, root_dir: Union[str, Path], lazy: bool = False) -> None:
        """Initialize the analyzer with a root directory.

        Args:
            root_dir: The root directory to start enumerating files from.
            lazy: If True, don't scan immediately. Use iter_files() instead.
                 If False (default), scan eagerly and store all results.

        Raises:
            FileNotFoundError: If the directory does not exist.
            NotADirectoryError: If the path is not a directory.
            PermissionError: If the directory cannot be accessed.
        """
        self.root_dir = Path(root_dir)

        # Validate input
        if not self.root_dir.exists():
            raise FileNotFoundError(f"Directory does not exist: {self.root_dir}")
        if not self.root_dir.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.root_dir}")

        # Try to access the directory to catch permission errors early
        try:
            # Attempt to list directory to verify we have read access
            next(self.root_dir.iterdir(), None)
        except PermissionError as e:
            raise PermissionError(f"Cannot access directory: {self.root_dir}") from e

        self._lazy = lazy
        self.file_count = 0
        self.dir_count = 0
        self.total_size = 0
        self.file_sizes: Dict[str, int] = {}

        if not lazy:
            self.enumerate_files()

    def enumerate_files(self) -> None:
        """Enumerate files in a directory and its subdirectories.

        Walks the directory tree and collects file sizes. Handles errors
        gracefully for inaccessible files or directories.

        Note: This loads all files into memory. For large filesystems,
        consider using iter_files() or iter_files_by_size() instead.
        """
        try:
            # Count the root directory itself
            if self.root_dir.is_dir():
                self.dir_count += 1

            # Walk through all items in the directory tree
            for item in self.root_dir.rglob("*"):
                if item.is_dir():
                    self.dir_count += 1
                elif item.is_file():
                    try:
                        size = item.stat().st_size
                        self.file_count += 1
                        self.file_sizes[str(item)] = size
                        self.total_size += size
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        pass
        except (OSError, PermissionError) as e:
            print(f"Warning: Cannot access {self.root_dir}: {e}", file=sys.stderr)

    def iter_files(self) -> Iterator[Tuple[Path, int]]:
        """Iterate over all files and their sizes without loading into memory.

        This is a memory-efficient alternative to enumerate_files() for large
        filesystems. Files are yielded as they are discovered.

        Yields:
            Tuple of (file_path, size_in_bytes) for each file found.

        Example:
            analyzer = FileSystemAnalyzer("/large/path", lazy=True)
            for file_path, size in analyzer.iter_files():
                if size > 1024**3:  # Files larger than 1GB
                    print(f"Large file: {file_path}")
        """
        try:
            for item in self.root_dir.rglob("*"):
                if item.is_file():
                    try:
                        size = item.stat().st_size
                        yield (item, size)
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        pass
        except (OSError, PermissionError) as e:
            print(f"Warning: Cannot access {self.root_dir}: {e}", file=sys.stderr)

    def iter_files_by_size(self,
                          top_n: Optional[int] = None,
                          reverse: bool = True) -> Iterator[Tuple[Path, int]]:
        """Iterate over files sorted by size without loading all into memory.

        This uses a heap to efficiently track the top N largest files without
        storing all files in memory. Perfect for finding space hogs in large
        filesystems.

        Args:
            top_n: If specified, only yield the top N files by size.
                  If None, yield all files sorted by size.
            reverse: If True (default), yield largest files first.
                    If False, yield smallest files first.

        Yields:
            Tuple of (file_path, size_in_bytes) sorted by size.

        Example:
            # Find top 10 largest files without loading everything
            analyzer = FileSystemAnalyzer("/large/path", lazy=True)
            for file_path, size in analyzer.iter_files_by_size(top_n=10):
                print(f"{file_path}: {size / (1024**3):.2f} GB")
        """
        if top_n is None:
            # No limit - collect all and sort
            files = list(self.iter_files())
            files.sort(key=lambda x: x[1], reverse=reverse)
            yield from files
        else:
            # Use heap to efficiently track top N
            # For largest files, use min heap (keeps smallest of the top N at root)
            # For smallest files, use max heap (keeps largest of the bottom N at root)
            heap: list[Tuple[int, Path]] = []

            for file_path, size in self.iter_files():
                if reverse:
                    # For largest files: use min heap, negate to simulate max heap
                    heap_size = -size
                else:
                    # For smallest files: use regular min heap
                    heap_size = size

                if len(heap) < top_n:
                    heapq.heappush(heap, (heap_size, file_path))
                elif heap_size > heap[0][0]:
                    heapq.heapreplace(heap, (heap_size, file_path))

            # Extract results and sort properly
            if reverse:
                # For largest files: negate back and sort descending
                results = sorted(
                    [(path, -heap_size) for heap_size, path in heap],
                    key=lambda x: x[1],
                    reverse=True
                )
            else:
                # For smallest files: sort ascending
                results = sorted(
                    [(path, heap_size) for heap_size, path in heap],
                    key=lambda x: x[1]
                )

            yield from results

    def get_file_size(self, file_path: str) -> int:
        """Return the size of a file given its file path.

        Args:
            file_path: The path to the file.

        Returns:
            The size of the file in bytes, or 0 if not found.

        Note:
            This only works if enumerate_files() was called (lazy=False).
            For lazy mode, use iter_files() instead.
        """
        return self.file_sizes.get(file_path, 0)

    def get_total_size(self) -> int:
        """Return the total size of all files.

        Returns:
            The total size in bytes.

        Note:
            This only works if enumerate_files() was called (lazy=False).
        """
        return self.total_size

    def print_top_consumers(self, num_top: int = 10) -> None:
        """Print the top consumers of disk space.

        Args:
            num_top: The number of top consumers to print. Defaults to 10.

        Note:
            For lazy mode, this will use iter_files_by_size() for efficiency.
            For eager mode, this uses the pre-loaded file_sizes dictionary.
        """
        if self._lazy or not self.file_sizes:
            # Use streaming approach
            for i, (file_path, size) in enumerate(
                self.iter_files_by_size(top_n=num_top), start=1
            ):
                print(f"{i}. {file_path}: {size / (1024**2):.2f} MB")
        else:
            # Use pre-loaded data
            sorted_sizes = sorted(
                self.file_sizes.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for i, (file_path, size) in enumerate(sorted_sizes[:num_top], start=1):
                print(f"{i}. {file_path}: {size / (1024**2):.2f} MB")

    def get_summary(self) -> str:
        """Return a summary report of the directory structure.

        Returns:
            A formatted string containing the summary report.

        Note:
            For lazy mode, this will scan the filesystem to gather stats.
        """
        if self._lazy and not self.file_sizes:
            # Calculate stats on the fly
            file_count = 0
            total_size = 0
            for _, size in self.iter_files():
                file_count += 1
                total_size += size

            return f"""
        Summary Report:
        ----------------
        Total Files: {file_count}
        Total Size: {total_size / (1024**2):.2f} MB
        """
        else:
            return f"""
        Summary Report:
        ----------------
        Total Files: {self.file_count}
        Total Directories: {self.dir_count}
        Total Size: {self.total_size / (1024**2):.2f} MB
        """


def example_enumerate(pathname: str) -> None:
    """Print the size of each file in the given directory.

    Args:
        pathname: The path of the directory to analyze.
    """
    analyzer = FileSystemAnalyzer(pathname)

    for file_path in analyzer.file_sizes.keys():
        file_size = analyzer.get_file_size(file_path)
        print(f"File {file_path} - File size: {file_size / 1024:.2f} KB")


def example_invocation(pathname: str) -> None:
    """Perform an analysis of a given pathname and print a summary.

    Args:
        pathname: The path to the directory to be analyzed.
    """
    analyzer = FileSystemAnalyzer(pathname)

    report = analyzer.get_summary()
    print(report)

    total_size = analyzer.get_total_size()
    print(f"Total size: {total_size / (1024**2):.2f} MB")

    analyzer.print_top_consumers()


def main() -> None:
    """Main entry point for the CLI."""
    num_args = len(sys.argv)

    if num_args != 2:
        print("ERROR: correct invocation:")
        print(f"\tzosdiskuse <pathname>")
        print(f"\t  or")
        print(f"\tpython3 -m zosdiskuse.usage <pathname>")
        sys.exit(1)

    example_invocation(sys.argv[1])
    example_enumerate(sys.argv[1])


if __name__ == "__main__":
    main()


