import pandas as pd

from loguru import logger
from dotenv import load_dotenv
from redminelib import Redmine
import os
from typing import List,Dict,Any,Literal,Optional
import glob

from RedmineIssueModel import RedmineIssueModel
from pydantic import  ValidationError

REDMINE_URL = 'https://gmvmine-southpan.gmv.com/redmine-ad/'

def get_excel_files(directory: str) -> List[str]:
    """Get all Excel files in the provided directory."""
    excel_files = glob.glob(f"{directory}/*.xlsx")
    # Remove file that starts with ~
    excel_files = [file for file in excel_files if not os.path.basename(file).startswith("~")]
    
    return excel_files


    
def display_results(inserted_issues: List[Any]):
    """Display the results."""
    for issue in inserted_issues:
        logger.info(f"Created issue {issue.id} in project {issue.project.name}.")
        

def main():
    """Main function to process Excel files and create Redmine issues."""
    directory = '.'  # Replace with your directory
    # Leer credenciales de .env
    load_dotenv()
    redmine_user = os.getenv("REDMINE_USER")
    redmine_password = os.getenv("REDMINE_PASSWORD")
    excel_files = get_excel_files(directory)


    processor = RedmineProcessor(redmine_user, redmine_password)
    results = processor(excel_files)
        
if __name__ == "__main__":
    main()
    
    