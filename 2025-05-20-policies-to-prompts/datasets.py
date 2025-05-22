import os
import requests
from pathlib import Path
import tarfile
import logging
import pymupdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url: str, output_path: Path) -> bool:
    """
    Download a file if it doesn't exist.
    Returns True if file was downloaded, False if it already existed.
    """
    if output_path.exists():
        logger.info(f"File already exists: {output_path}")
        return False
    
    logger.info(f"Downloading {url} to {output_path}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return True

def extract_tar(tar_path: Path, extract_path: Path) -> bool:
    """
    Extract a tar file if the target directory doesn't exist.
    Returns True if extraction was performed, False if already extracted.
    """
    if extract_path.exists():
        logger.info(f"Directory already exists: {extract_path}")
        return False
    
    logger.info(f"Extracting {tar_path} to {extract_path}")
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=extract_path)
    
    return True

def convert_pdf_to_text(pdf_path: Path, text_path: Path) -> bool:
    """
    Convert a PDF file to text.
    Returns True if conversion was performed, False if already converted.
    """
    if text_path.exists():
        logger.info(f"File already exists: {text_path}")
        return False
    
    logger.info(f"Converting {pdf_path} to text")
    try:
        # Open the PDF
        doc = pymupdf.open(pdf_path)
        text = ""
        
        # Extract text from each page
        for page in doc:
            text += page.get_text()
        
        # Write the text to file
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        doc.close()
        return True
    except Exception as e:
        logger.error(f"Error converting PDF to text: {e}")
        return False

def main():
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Download Enron email dataset
    enron_url = "https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
    enron_tar = data_dir / "enron_mail_20150507.tar.gz"
    enron_extract = data_dir / "enron_mail_20150507"
    
    download_file(enron_url, enron_tar)
    extract_tar(enron_tar, enron_extract)
    
    # Download Sarbanes-Oxley rules
    sox_url = "https://www.govinfo.gov/content/pkg/PLAW-107publ204/html/PLAW-107publ204.htm"
    sox_path = data_dir / "sarbanes_oxley.htm"
    download_file(sox_url, sox_path)
    
    # Download JPMC Code of Conduct
    jpmc_url = "https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/documents/code-of-conduct.pdf"
    jpmc_path = data_dir / "jpmc_code_of_conduct.pdf"
    download_file(jpmc_url, jpmc_path)
    convert_pdf_to_text(jpmc_path, data_dir / "jpmc_code_of_conduct.txt")


if __name__ == "__main__":
    main()