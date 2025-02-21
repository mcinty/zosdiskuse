# Contributing to zosdiskusage

Thank you for taking the time to contribute to zosdiskuse.  Let's keep this simple and follow this process:

- https://github.com/firstcontributions/first-contributions

All contributions should be made under the same license as the project.

## Ways to Contribute

You can write code, work on the documentation, provide tests, report bugs or provide suggestions for improvement.

### Coding

Pay attention to the prevailing style in the code, and make liberal use of flake8 and pycodestyle.

## Building

Building the source and built distributions:

```sh
$ python3 -m venv venv
$ . venv/bin/activate
$ pip3 install -r requirements.txt
$ python3 -m build
```

### Testing

Build the package as per above, and install it in a clean virtual environment.

Then use pytest to run the suite from the project root directory:

```sh
$ pip3 -r install requirements.txt
$ pytest
```

