from redminelib import Redmine
from dotenv import load_dotenv
import os
# load .env file
load_dotenv()

redmine_user= os.getenv("REDMINE_USER")
redmine_password= os.getenv("REDMINE_PASSWORD")
redmine_url= os.getenv("REDMINE_URL")


redmine = Redmine(redmine_url, username=redmine_user, password=redmine_password)


fields = redmine.custom_field.all(limit =5)
try : 
    for field in fields:
        print(field.id, field.name)
        a = a + 1    
except Exception as e:
    pass
    
a = 0
# List projects
for project in redmine.project.all():
    print("proyecto:", project.id, project.name)
    custom_fields = project.custom_fields
    for custom_field in custom_fields:
        print(custom_field.id, custom_field.name)
        a = a + 1




# List the custom fields for a given redmine project
project = redmine.project.get('SouthPAN_GASS')
custom_fields = project.custom_fields
for custom_field in custom_fields:
    print(custom_field.id, custom_field.name)
    a = a + 1
