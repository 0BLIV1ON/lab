# Hidden File and Directory Scanner

This project provides tools to generate wordlists focused on common web directories and files, and to scan a target URL for hidden files and directories.

## Features

- Generate customizable wordlists for directory enumeration.
- Scan a target URL to discover hidden files and directories, including admin panels.
- Save found paths to a file for later reference.

## Requirements

- Python 3.12 or higher
- Required libraries: `colorama`, `requests`

## Installation

Clone the repository and install the required libraries:

```bash
pip install -r requirements.txt
```

## Usage
To generate a wordlist, run:

```bash
python generator.py -o <output_filename> -c <number_of_words> --numbers
```

To scan a target URL for hidden files and directories, run:


```bash
python main.py
```

You will be prompted to enter the target URL.

## Customization
You can customize the wordlist generation by altering the parameters in generator.py. The current configurations include common paths and files that are often targeted during web security assessments.

## Contributing
Feel free to submit pull requests or report issues.
