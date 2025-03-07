"""
Zotero OCR to Markdown 

This is a command line tool that takes in the csv generated from Zotero export function and, for those entries where a PDF is available, it parses it associated into markdown documents and dictionaries containing markdown per page.The outputs are saved using the Zotero entry key as the file name.

This tool uses the Mistral's OCR model via API calls. Average processing speed is between 5 and 10 seconds per PDF.
"""

import pandas as pd
import argparse
import re
import json
import sys
import os
import re

from pathlib import Path
from mistralai import DocumentURLChunk, Mistral
from tqdm import tqdm


def library_import(library_directory):
    """
    Function that imports the Zotero library and derives the paths of each pdf file

    Input: 
        library_directory (str): path directory of the csv exported from Zotero

    Output: 
        df (Pandas dataframe): cleaned zotero dataframe 
        paths (list): all the paths to the pdfs 
    """
    try:
        df = pd.read_csv(library_directory)

        paths = df[df['File Attachments'].notna()]['File Attachments']
        paths = paths.str.split(';')
        paths = paths.explode()
        paths = paths[paths.str.contains('.pdf')]  # select only those referring to pdfs
        paths = [s[1:] if s.startswith(" ") else s for s in paths]

        df = df[df['File Attachments'].notna()]
        pattern = '|'.join(map(re.escape, paths))
        df = df[df['File Attachments'].str.contains(pattern, na=False)]
        
        return df, paths
    
    except Exception as e:
        print(f"Error importing library: {e}")
        return pd.DataFrame(), []


def mistral_api(api_key):
    """
    Mistral client setup
    """
    try:
        client = Mistral(api_key=api_key)
        return client
    except Exception as e:
        print(f"Error setting up Mistral client: {e}")
        return None


def pdf_ocr(path, client):
    """
    Function that uses the Mistral OCR model to parse pdfs into markdown files

    Input: 
        path (str): Path to the PDF file
        client: Mistral client instance

    Output: 
        response_dict (dict): dictionary with the parsed OCR results
        json_string (str): the same dictionary in string format
        full_markdown (str): the full markdown string
    """
    try:
        pdf_file = Path(path)
        
        uploaded_file = client.files.upload(
            file={
                "file_name": pdf_file.stem,
                "content": pdf_file.read_bytes(),
            },
            purpose="ocr",
        )
        
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        
        pdf_response = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url), 
            model="mistral-ocr-latest", 
            include_image_base64=False
        )
        
        response_dict = json.loads(pdf_response.json())
        json_string = json.dumps(response_dict, indent=4)

        full_markdown = " ".join(page["markdown"] for page in response_dict["pages"])
        
        return response_dict, json_string, full_markdown
    
    except Exception as e:
        print(f"Error processing PDF {path}: {e}")
        raise


def save_file(response_dict, markdown, output_directory, file_name):
    """
    Function that takes the dictionary and markdown and saves it to the disk

    Input: 
        response_dict (dict): OCR response dictionary
        markdown (str): Markdown text
        output_directory (str path): Directory to save outputs
        file_name (str): Name of the file
    """
    try:
        os.makedirs(os.path.join(output_directory, 'json/'), exist_ok=True)
        os.makedirs(os.path.join(output_directory, 'markdown/'), exist_ok=True)

        json_dir = os.path.join(output_directory, 'json/')
        md_dir = os.path.join(output_directory, 'markdown/')
        
        json_file = os.path.join(json_dir, f"{file_name}.json")
        md_file = os.path.join(md_dir, f"{file_name}.md")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(response_dict, f, ensure_ascii=False, indent=2)

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(markdown)
            
    except Exception as e:
        print(f"Error saving files: {e}")
        raise


def write_log(output_directory, processed_files, saved_files, errors):
    """
    Function to write the log file in the output_directory
    """
    try:
        # Clean the files if they exist
        file_names = ["processed_files.txt", "saved_files.txt", "failed_files.txt"]
        for file_name in file_names:
            file_path = os.path.join(output_directory, file_name)
            if os.path.exists(file_path):
                open(file_path, "w").close()
                
        # write files
        with open(os.path.join(output_directory, "processed_files.txt"), "w", encoding='utf-8') as f:
            for item in processed_files:
                f.write(f"{item}\n")
        with open(os.path.join(output_directory, "saved_files.txt"), "w", encoding='utf-8') as f:
            for item in saved_files:
                f.write(f"{item}\n")
        with open(os.path.join(output_directory, "failed_files.txt"), "w", encoding='utf-8') as f:
            for item in errors:
                f.write(f"{item}\n")
                
    except Exception as e:
        print(f"Error writing log files: {e}")


def process_pdfs(library_path, output_directory, api_key):
    """
    Main function combining the pipeline.     
    """
    # Import library and derive paths
    df, paths = library_import(library_path)

    # Set up mistral api client 
    client = mistral_api(api_key)

    # Initialise empty lists for log
    processed_files = []
    saved_files = []
    errors = []

    # Run loop over all existing paths in the Zotero library
    for path in tqdm(paths, desc="Processing PDFs", unit="file"):
        try: 
            row_df = df[df['File Attachments'].str.contains(re.escape(path), na=False)].reset_index(drop=True)
                
            file_name = row_df["Key"].values[0] 
            title = row_df["Title"].values[0]         
            
            response_dict, json_string, markdown = pdf_ocr(path, client)
            processed_files.append(title)
           
            save_file(response_dict, markdown, output_directory, file_name)
            saved_files.append(title)
            
        except Exception as e:
            if 'title' in locals():
                errors.append(title)
                errors.append(e)
            else:
                errors.append(path)
                errors.append(e)

    write_log(output_directory, processed_files, saved_files, errors)

    print(f'Successfully processed {len(processed_files)} PDF files from the {library_path} library and '
          f'saved {len(saved_files)} to {output_directory} with {len(errors)} errors. '
          f'See the log files at {output_directory} for more details.')
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDFs to Markdown using Mistral OCR API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-l", "--library", required=True, help="Path to Zotero library CSV file")
    parser.add_argument("-o", "--output", required=True, help="Directory to save output files")
    parser.add_argument("-k", "--api-key", required=True, help="Mistral API key")
    
    args = parser.parse_args()
    
    # Validate paths
    if not os.path.isfile(args.library):
        print(f"Error: Library file not found at {args.library}")
        return 1
        
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Run the processing
    success = process_pdfs(args.library, args.output, args.api_key)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())