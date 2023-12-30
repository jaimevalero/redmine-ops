import pandas as pd

from loguru import logger
from dotenv import load_dotenv
from redminelib import Redmine
import os
from typing import List,Dict,Any,Literal,Optional
import glob
from pydantic import BaseModel, ValidationError

REDMINE_URL = 'https://gmvmine-southpan.gmv.com/redmine-ad/'

def get_excel_files(directory: str) -> List[str]:
    """Get all Excel files in the provided directory."""
    excel_files = glob.glob(f"{directory}/*.xlsx")
    # Remove file that starts with ~
    excel_files = [file for file in excel_files if not os.path.basename(file).startswith("~")]
    
    return excel_files

def load_excel_into_dataframe(file_path: str) -> pd.DataFrame:
    """Load the first sheet of an Excel file into a pandas DataFrame."""
    return pd.read_excel(file_path)

from pydantic import BaseModel, Field
from typing import Literal

class IssueModel(BaseModel):
    Code: str = Field(alias="Code")
    Subject: str = Field(alias="Subject")
    Description: str = Field(alias="Description")
    Status: Literal["Open", "Assigned", "Answered", "Closed", "Rejected", "Closed with Action", "Closed with No Action", "Implemented"] = Field(alias="Status")
    Priority: str = Field(alias="Priority")
    Target_version: str = Field(alias="Target version")
    Originator_Company: str = Field(alias="Originator Company")
    RID_Category: str = Field(alias="RID Category")
    Problem_Location: str = Field(alias="Problem Location")
    Recommended_Solution: str = Field(alias="Recommended Solution")
    Parent_task: int = Field(alias="Parent task")
    Assignee: str = Field(alias="Assignee")
    Reply_from_the_Responsible: Optional[str] = Field(alias="Reply from the Responsible")
    Action_to_implement: Optional[str] = Field(alias="Action to implement")    
    Project: str = Field(alias="Project")
    # Add more fields if necessary

def validate_dataframe(df: pd.DataFrame,redmine) -> bool:
    """Validate and process the DataFrame."""
    if df.empty:
        logger.error("The DataFrame is empty.")
        raise ValueError("The DataFrame has no data to process.")
    # List all Redmine projects
    redmine_projects = [ project.name for project in redmine.project.all()]
    # Project columns has to be in the list of Redmine projects    
    if "Project" not in df.columns:
        logger.error("The DataFrame has no Project column.")
        raise ValueError("The DataFrame has no Project column.")
    # Check if all projects in the DataFrame are in Redmine
    if not df["Project"].isin(redmine_projects).all():
        logger.error("The DataFrame has invalid projects.")
        raise ValueError("The DataFrame has invalid projects.")
    

    for index, row in df.iterrows():
        row_dict = row.to_dict()
        row_dict = {k: v if pd.notna(v) else None for k, v in row_dict.items()}
        try:
            issue = IssueModel(**row_dict)
            # Process the issue here
        except ValidationError as e:
            logger.error(f"Invalid data in row {index}: {e}")
            raise ValueError(f"Invalid data in row {index}")
        
    logger.info(f"All rows in the DataFrame are valid. Size is {df.shape}")
    return True

def process_dataframe(df: pd.DataFrame, redmine: Redmine) -> Dict[int, Dict[str, Any]]:
    """Iterate over each row in the DataFrame and create a Redmine issue."""
    issues = {}
    TRACKER_ID_RID = 18
    inserted_issues = []
    for index, row in df.iterrows():
        row_dict = row.to_dict()
        row_dict = {k: v if pd.notna(v) else None for k, v in row_dict.items()}
        try:
            issue = IssueModel(**row_dict)
            issue.Project = issue.Project.lower()
            redmine_project_id = redmine.project.get(issue.Project).id
        
            # Get user in the project
            users = redmine.project_membership.filter(project_id=redmine_project_id)
            users_formatted = { user["user"]["name"]: user["user"]["id"] for user in users   }
            
            status = redmine.issue_status.all()
            status_formatted = { status.name: status.id for status in status   }
            target_versions = {target_version.name: target_version.id for target_version in redmine.version.filter(project_id=redmine_project_id)}                
            
            inserted_issue = redmine.issue.create(
                project_id=redmine_project_id,#
                tracker_id=TRACKER_ID_RID, 
                status_id=status_formatted[issue.Status],#
                assigned_to_id=users_formatted[issue.Assignee],
                fixed_version_id =target_versions[issue.Target_version],#
                subject=issue.Subject, #
                description=issue.Description, #
                parent_issue_id=issue.Parent_task,
                custom_fields=[   
                    {'id': 1, 'name': 'Code', 'value': issue.Code},                
                    {'id': 99, 'name': 'Originator Company', 'value': issue.Originator_Company}, 
                    {'id': 104, 'name': 'Problem Location', 'value': issue.Problem_Location},
                    {'id': 105, 'name': 'Recommended Solution', 'value': issue.Recommended_Solution}, 
                    {'id': 106, 'name': 'Reply from the Responsible', 'value': issue.Reply_from_the_Responsible}, 
                    {'id': 107, 'name': 'Action to Implement', 'value': issue.Action_to_implement}
                    ] )
            if inserted_issue: 
                inserted_issues.append(inserted_issue)
                  
                  
                                
            logger.info(f"Created issue {inserted_issue.id} in project {issue.Project}.")
        except ValidationError as e:
            logger.exception(f"Invalid data in row {index}: {e}")
            
    logger.info(f"Processed {len(issues)} issues.")
    return inserted_issues

def display_results(inserted_issues: List[Any]):
    """Display the results."""
    for issue in inserted_issues:
        logger.info(f"Created issue {issue.id} in project {issue.project.name}.")
        
    # TODO: Implement this function
def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the DataFrame."""
    # Drop the Code column if it exists
    if "Code" in df.columns:
        df.drop(columns=["Code"], inplace=True)
    # rename column ID to Code
    df.rename(columns={"Id": "Code"}, inplace=True)
    # Replace all nan values with None
    df = df.where(pd.notnull(df), None)
    # If column Recommended Solution is empty, fill empty values with -
    if "Recommended Solution" in df.columns:
        df["Recommended Solution"].fillna("-", inplace=True)
        # Replace character "𝑓" for "f" in Recommended Solution column
        df["Recommended Solution"] = df["Recommended Solution"].str.replace("𝑓", "f")
    # If column Problem Location is empty, fill empty values with -
    if "Problem Location" in df.columns:
        df["Problem Location"].fillna("-", inplace=True)

    
    
    return df

def process_files_redmine(excel_files, redmine_user: str, redmine_password: str):
    """Process a single file."""

    redmine_url = "https://gmvmine-southpan.gmv.com/redmine-ad/" 
    redmine = Redmine(redmine_url, username=redmine_user ,password=redmine_password)
    results = None
    for excel_file in excel_files:
        try:
            logger.info(f"Processing file {excel_file}")
            df = load_excel_into_dataframe(excel_file)
            df = preprocess_dataframe(df)
            validate_dataframe(df,redmine)
            inserted_issues = process_dataframe(df, redmine)
            results = display_results(inserted_issues)
        except Exception as e:
            logger.exception(f"Error processing file {excel_file}: {str(e)}")
            pass
    return results
    
def main():
    """Main function to process Excel files and create Redmine issues."""
    directory = '.'  # Replace with your directory
    # Leer credenciales de .env
    load_dotenv()
    redmine_user = os.getenv("REDMINE_USER")
    redmine_password = os.getenv("REDMINE_PASSWORD")
    #redmine_url = os.getenv("REDMINE_URL")
    
    redmine_url = "https://gmvmine-southpan.gmv.com/redmine-ad/" 
    
    redmine = Redmine(redmine_url, username=redmine_user ,password=redmine_password)

    excel_files = get_excel_files(directory)

    for excel_file in excel_files:
        try:
            df = load_excel_into_dataframe(excel_file)
            df = preprocess_dataframe(df)
            validate_dataframe(df,redmine)
            inserted_issues = process_dataframe(df, redmine)
            display_results(inserted_issues)
        except Exception as e:
            logger.exception(f"Error processing file {excel_file}: {str(e)}")
            pass
if __name__ == "__main__":
    main()
    
    