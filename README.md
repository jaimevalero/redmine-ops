# Redmine Ops
Redmine Ops is a Python module designed to import issues into Redmine from an Excel file. 

> ⚠️ **WARNING: Please note that this module is dependent on the custom fields in an specific Redmine instance, and therefore, it is not a general-purpose module.**

## Required Fields in Excel File
The Excel file should contain the following fields, which correspond to the attributes of the Pydantic model:

| Field                   | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `Code`                  | A unique identifier for the issue.                                          |
| `Subject`               | The title of the issue.                                                     |
| `Description`           | A detailed description of the issue.                                        |
| `Status`                | The current status of the issue. Can be one of the following: "Open", "Assigned", "Answered", "Closed", "Rejected", "Closed with Action", "Closed with No Action", "Implemented". |
| `Priority`              | The priority level of the issue.                                            |
| `Target version`        | The target version for the issue resolution.                                |
| `Originator Company`    | The company that originated the issue.                                      |
| `RID Category`          | The category of the issue.                                                  |
| `Problem Location`      | The location where the problem occurred.                                    |
| `Recommended Solution`  | The recommended solution for the issue.                                     |
| `Parent task`           | The ID of the parent task.                                                  |
| `Assignee`              | The person assigned to the issue.                                           |
| `Reply from the Responsible` | The reply from the responsible person (optional).                      |
| `Action to implement`   | The action to be implemented (optional).                                    |
| `Project`               | The project the issue belongs to.                                           |

## Running the Application
To run this application, you need to have Python installed on your machine. Follow these steps:

1. Clone the repository.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Choose one of the followings methods to run the application.
    - Execute the .exe file 
    - Run the application with `python tkinter_app.py` command.
    - Raise the flask application with `python app.py` command and open the application in a browser.
    - Execute the headless application with `python redmine_helpers.py` command.

## Packaging as an Executable
To package the application as an executable file, you can use PyInstaller with the following command:

```sh
pyinstaller --onefile --windowed tkinter_app.py

```
