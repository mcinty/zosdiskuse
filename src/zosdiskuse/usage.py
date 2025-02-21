import os
import sys


class FileSystemAnalyzer:

    def __init__(self, root_dir):
        """
        Initializes the instance of the class.

        Parameters:
        root_dir (str): The root directory to start enumerating files from.

        Returns:
        None
        """
        self.root_dir = root_dir
        self.file_count = 0
        self.dir_count = 0
        self.total_size = 0
        self.file_sizes = {}
        self.enumerate_files()

    def enumerate_files(self):
        """
        Enumerate files in a directory and its subdirectories.

        Parameters:
        root_dir (str): The root directory to start enumerating from.

        Returns:
        dir_count (int): The total number of directories encountered.
        file_count (int): The total number of files encountered.
        file_sizes (dict): A dictionary mapping file paths to their sizes.
        total_size (int): The total size of all files encountered.
        """
        for root, dirs, files in os.walk(self.root_dir):
            self.dir_count += 1
            for file in files:
                file_path = os.path.join(root, file)
                self.file_count += 1
                self.file_sizes[file_path] = os.path.getsize(file_path)
                self.total_size += os.path.getsize(file_path)

        return

    def get_file_size(self, file_path):
        """
        Returns the size of a file given its file path.

        Parameters:
        file_path (str): The path to the file.

        Returns:
        int: The size of the file in bytes.
        """
        return self.file_sizes.get(file_path, 0)

    def get_total_size(self):
        """
        Returns the total size of the object.

        Args:
            self (Object): The object to calculate the total size of.

        Returns:
            int: The total size of the object in bytes.
        """
        return self.total_size

    def print_top_consumers(self, num_top=10):
        """
        Prints the top consumers of disk space.

        Parameters:
        self (DiskUsageAnalyzer): The instance of the DiskUsageAnalyzer class.
        num_top (int, optional): The number of top consumers to print.
                                 Defaults to 10.

        Returns:
        None
        """
        sorted_sizes = sorted(self.file_sizes.items(),
                              key=lambda x: x[1],
                              reverse=True)
        for i, (file_path, size) in enumerate(sorted_sizes[:num_top]):
            print(f"{i+1}. {file_path}: {size / (1024**2):.2f} MB")

        return

    def get_summary(self):
        """
        Returns a summary report of the directory structure.

        Parameters:
        self (DirectorySummary): An instance of the DirectorySummary class.

        Returns:
        str: A formatted string containing the summary report.
        """
        return f"""
        Summary Report:
        ----------------
        Total Files: {self.file_count}
        Total Directories: {self.dir_count}
        Total Size: {self.total_size / (1024**2):.2f} MB
        """


def example_enumerate(pathname):
    """
    This function prints the size of each file in the given directory.

    Args:
        pathname (str): The path of the directory to analyze.

    Returns:
        None
    """
    analyzer = FileSystemAnalyzer(pathname)

    f = analyzer.file_sizes.keys()
    for i in f:
        file_size = analyzer.get_file_size(i)
        print(f"File {i} - File size: {file_size / 1024:.2f} KB")

    return


def example_invocation(pathname):
    """
    This function performs an analysis of a given pathname and
    prints a summary of the files and directories found.

    Args:
        pathname (str): The path to the directory to be analyzed.

    Returns:
        None
    """
    analyzer = FileSystemAnalyzer(pathname)

    report = analyzer.get_summary()
    print(report)

    total_size = analyzer.get_total_size()
    print(f"Total size: {total_size / (1024**2):.2f} MB")

    analyzer.print_top_consumers()

    return


if __name__ == "__main__":

    n = len(sys.argv)

    if n != 2:
        print("ERROR:  correct invocation:")
        print(f"\tpython3 {sys.argv[0]} <pathname>")
        exit(1)

    example_invocation(sys.argv[1])
    example_enumerate(sys.argv[1])
