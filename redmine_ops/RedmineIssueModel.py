import pandas as pd

from loguru import logger
from redminelib import Redmine
import os
from typing import List,Dict,Any,Literal,Optional
import glob
from pydantic import BaseModel, ValidationError,model_validator,ConfigDict  ,Field

class RedmineIssueModel(BaseModel):
    """ Class that validates the data from the Excel file and creates a Redmine issue."""
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)

    @model_validator(mode='before')
    @classmethod
    def validate_assignee_exists(self, v):
        """
        Validate that the assignee exists in Redmine.
        """
        redmine = v.get("redmine")
        assignee = v.get("Assignee")
        project_name = v.get("Project")
        users = redmine.project_membership.filter(project_id=redmine.project.get(project_name).id)
        users_formatted = [user["user"]["name"] for user in users]
        if assignee not in users_formatted:
            raise ValueError(f"{assignee} is not a valid assignee in Redmine. Valid values are {users_formatted}")
        return v

    @model_validator(mode='before')
    @classmethod
    def validate_project_exists(self, v):
        """
        Validate that the project exists in Redmine.
        """
        redmine = v.get("redmine")
        project_name = v.get("Project")
        valid_projects = [project.name for project in redmine.project.all()]
        if project_name not in valid_projects:
            raise ValueError(f"{project_name} is not a valid project in Redmine. Valid projects are {valid_projects}")
        return v

    @model_validator(mode='before')
    @classmethod
    def validate_parent_task_exists(self, v):
        """
        Validate that the parent task exists in Redmine.
        """
        redmine = v.get("redmine")
        parent_task = v.get("Parent_task")
        if parent_task:
            try:
                redmine.issue.get(parent_task)
            except Exception:
                raise ValueError(f"The parent task {parent_task} does not exist in Redmine")
        return v

    @classmethod
    def validate_fixed_version_id_exists(self, v):
        redmine = v.get("redmine")
        fixed_version_id = v.get("Target_version")
        if fixed_version_id:
            try:
                redmine.version.get(fixed_version_id)
            except Exception:
                raise ValueError(f"The fixed version {fixed_version_id} does not exist in Redmine")
        return v
                    
    Code: str = Field(alias="Code")
    Subject: str = Field(alias="Subject")
    Description: str = Field(alias="Description")
    Status: Literal["Open", "Assigned", "Answered", "Closed", "Rejected", "Closed with Action", "Closed with No Action", "Implemented"] = Field(alias="Status")
    Priority: str = Field(alias="Priority")
    Target_version: str = Field(alias="Target version",pre=validate_fixed_version_id_exists)
    Originator_Company: str = Field(alias="Originator Company")
    RID_Category: str = Field(alias="RID Category")
    Problem_Location: str = Field(alias="Problem Location")
    Recommended_Solution: str = Field(alias="Recommended Solution")
    Parent_task: int = Field(alias="Parent task", pre=validate_parent_task_exists)
    Assignee: str = Field(alias="Assignee", pre=validate_assignee_exists)
    Reply_from_the_Responsible: Optional[str] = Field(alias="Reply from the Responsible")
    Action_to_implement: Optional[str] = Field(alias="Action to implement")    
    Project: str = Field(alias="Project",pre=validate_project_exists)
    
