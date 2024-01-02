
import pandas as pd

from loguru import logger
from dotenv import load_dotenv
from redminelib import Redmine
import os
from typing import List,Dict,Any,Literal,Optional
import glob
from redmine_ops.RedmineIssueModel import RedmineIssueModel

from pydantic import  ValidationError

class RedmineProcessor:
    """    A class to handle the processing of Excel files and issue creation in Redmine.

        This class is responsible for preparing the Redmine object, preprocessing DataFrame data,
        validating the data, and processing Excel files to create issues in Redmine.

        Attributes:
            redmine (Redmine): The Redmine object prepared for interaction with the Redmine API.
    """
    def __init__(self, redmine_user: str, redmine_password: str):
        self.redmine_url = "https://gmvmine-southpan.gmv.com/redmine-ad/" 
        self.redmine = self.prepare_redmine(
            redmine_user, 
            redmine_password,
            self.redmine_url)

    def prepare_redmine(self, redmine_user: str, redmine_password: str,redmine_url: str):
        """Prepare the Redmine object."""
        redmine = Redmine(url=redmine_url, username=redmine_user ,password=redmine_password)
        return redmine

    def preprocess_dataframe(self,df: pd.DataFrame) -> pd.DataFrame:
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

    def load_excel_into_dataframe(self,file_path: str) -> pd.DataFrame:
        """Load the first sheet of an Excel file into a pandas DataFrame."""
        return pd.read_excel(file_path)
        
    def process_files_redmine(self, excel_files):
        """Process a list of Excel files."""
        inserted_issues = None
        for excel_file in excel_files:
            try:
                logger.info(f"Processing file {excel_file}")
                df = self.load_excel_into_dataframe(excel_file)
                df = self.preprocess_dataframe(df)
                invalid_rows = self.validate_dataframe(df, self.redmine)
                inserted_issues = self.process_dataframe(df, self.redmine)
                formatted_results = self.display_results(inserted_issues)
            except Exception as e:
                logger.exception(f"Error processing file {excel_file}: {str(e)}")
                pass
        return formatted_results
    
    def display_results(self,inserted_issues: List[Any]):
        """Display the results."""
        results = []
        for issue in inserted_issues:
            results.append({
                    "id": issue.id, 
                    "project": issue.project.name,
                    "subject": issue.subject,
                    })
            logger.info(f"Created issue {issue.id} in project {issue.project.name}.")
        return results            
        
    def validate_dataframe(self,df: pd.DataFrame,redmine) -> bool:
        """Validate and process the DataFrame."""
        if df.empty:
            logger.error("The DataFrame is empty.")
            raise ValueError("The DataFrame has no data to process.")
        invalid_rows = 0
        for index, row in df.iterrows():
            row_dict = {k: v if pd.notna(v) else None for k, v in row.to_dict().items()}
            try:
                issue = RedmineIssueModel(**row_dict, redmine=redmine)
            except ValidationError as e:
                logger.error(f"Invalid data in row {index}: {e}")
                invalid_rows += 1        
        logger.info(f"Invalid rows: {invalid_rows} / {df.shape[0]}")
        return invalid_rows

    def __call__(self, excel_files):
        """Make the class callable to hide implementation details."""
        results = self.process_files_redmine(excel_files) 
        return results
 
    def __enter__(self):
        # Preparar el procesador (por ejemplo, conectar con la API de Redmine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Limpiar los recursos (por ejemplo, cerrar la conexión con la API de Redmine)
        pass   


    def process_dataframe(self,df: pd.DataFrame, redmine: Redmine) -> Dict[int, Dict[str, Any]]:
        """Iterate over each row in the DataFrame and create a Redmine issue."""
        issues = {}
        TRACKER_ID_RID = 18
        inserted_issues = []
        for index, row in df.iterrows():
            row_dict = row.to_dict()
            row_dict = {k: v if pd.notna(v) else None for k, v in row_dict.items()}
            try:
                issue = RedmineIssueModel(**row_dict, redmine=redmine)
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

