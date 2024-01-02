import pandas as pd

from loguru import logger
from dotenv import load_dotenv
import os
from typing import List,Dict,Any,Literal,Optional
import glob
from pydantic import  ValidationError
from redmine_ops.RedmineProcessor import RedmineProcessor

def get_excel_files(directory: str) -> List[str]:
    """Get all Excel files in the provided directory."""
    excel_files = glob.glob(f"{directory}/*.xlsx")

    # remove that start with ~ or has "tmptmp" in the name
    excel_files = [file for file in excel_files if not ("\\~") in file ] 
    excel_files = [file for file in excel_files if not ("tmptmp") in file ]
    return excel_files


    



def main():
    """Main function to process Excel files and create Redmine issues."""
    directory = '.'  # Replace with your directory
    # Leer credenciales de .env
    load_dotenv()
    redmine_user = os.getenv("REDMINE_USER")
    redmine_password = os.getenv("REDMINE_PASSWORD")
    excel_files = get_excel_files(directory)
    results = []
    with RedmineProcessor(redmine_user, redmine_password) as processor:
        results = processor(excel_files)
    a = 0
        
if __name__ == "__main__":
    main()
    
    