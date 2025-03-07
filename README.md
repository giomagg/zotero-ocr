# Zotero OCR 

This is a command-line tool to parses PDF files associated to a Zotero library into Markdown format using Mistral's OCR model via API. It takes in the csv generated from Zotero export function and, for those entries where a PDF is available, it parses the associated PDF into markdown documents and json files (markdown per page). 

Average processing speed via the Mistral API is around 5 - 10 seconds per PDF. 

## Features

- Process PDFs from a Zotero library export
- Convert PDFs to markdown format using Mistral's OCR API
- Save both JSON (raw OCR output) and Markdown versions
- Track processing success and failures in log files

## Installation

### Prerequisites

- Python 3.8 or higher
- A Mistral API key

### Install from GitHub

```bash
# Clone the repository
git clone https://github.com/giomagg/zotero-ocr.git
cd zotero-ocr

# Install the package
pip install -e .
```

## Usage

### Basic Usage

```bash
mistral-ocr --library path/to/zotero_library.csv --output path/to/output_directory --api-key your_mistral_api_key
```

### Command Line Arguments

- `-l`, `--library`: Path to the Zotero library CSV file (required)
- `-o`, `--output`: Directory to save output files (required)
- `-k`, `--api-key`: Mistral API key (required)

### Example

```bash
mistral-ocr -l ~/Desktop/zotero_library.csv -o ~/Desktop/ocr_output -k "your-mistral-api-key"
```

## Preparing Your Zotero Library

1. In Zotero, go to File > Export Library
2. Choose "CSV" as the format
3. Make sure to select "Export Files" if you want to include attachments
4. Save the CSV file
5. Use the path to this CSV file as the `--library` parameter

## Output Structure

The tool creates the following structure in your output directory:

```
output_directory/
├── json/              # Raw OCR output in JSON format
├── markdown/          # Converted markdown files
├── processed_files.txt # List of all files that were processed
├── saved_files.txt    # List of all files that were successfully saved
└── failed_files.txt   # List of files that encountered errors
```

## Troubleshooting

If you encounter issues:

1. Check that your Mistral API key is valid
2. Ensure your Zotero library CSV contains the correct file paths
3. Verify that the PDF files exist at the specified locations
4. Review the logs in the output directory for specific errors

## License

MIT

## Credits

This tool was created to make it easier to convert academic papers and other documents to markdown format for improved accessibility and text analysis.
