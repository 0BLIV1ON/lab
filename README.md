# Directory Scanner and Wordlist Generator

This project provides tools to generate wordlists focused on common web directories and files, and to scan a target URL for hidden files and directories.

## Features

- Generate a comprehensive wordlist with customizable options
- Scan a target URL for existing directories and files
- Support for threading to enhance scanning performance
- Include options for number variations in the wordlist

## Usage

### Wordlist Generation

To generate a wordlist, you can use the following command:

```bash
python generator.py --output <output_filename> --count <number_of_words> --numbers