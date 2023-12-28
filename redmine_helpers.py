from redminelib import Redmine
from dotenv import load_dotenv
import os
# load .env file
load_dotenv()

redmine_user= os.getenv("REDMINE_USER")
redmine_password= os.getenv("REDMINE_PASSWORD")
redmine_url= os.getenv("REDMINE_URL")


redmine = Redmine(redmine_url, username=redmine_user, password=redmine_password)

a = 0
# List projects
for project in redmine.project.all():
    print(project.id, project.name)
    a = a + 1
a = 0