from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from loguru import logger
from typing import List
from werkzeug.datastructures import FileStorage
import os

from redmine_ops.RedmineProcessor import RedmineProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key-that-should-be-changed'  # replace with your secret key
Bootstrap(app)

class UploadForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    files = FileField('Files', validators=[DataRequired()])

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    form = UploadForm()
    if form.validate_on_submit():
        # get username and password
        username: str = form.username.data
        password: str = form.password.data

        # get files
        files: List[FileStorage] = request.files.getlist('files')

        # process files
        try:
            with RedmineProcessor(username, password) as processor:
                excel_files = process_files( files)
                results = processor(excel_files)
                
        except Exception as e:
            logger.exception(f"Error processing files: {str(e)}")
            return "Error processing files", 500
        # render results template
        return render_template('results.html', results=results)
        
        
        
        
    return render_template('index.html', form=form)

def process_files(files: List[FileStorage]):
    """Process uploaded files."""
    file_paths = []
    for file in files:
        # Convert the FileStorage to a local temp file
        try : 
            logger.info(f"Processing file {file.filename}")
            filename = secure_filename(file.filename)
            if os.path.exists(f"tmptmp-{filename}"):
                os.remove(f"tmptmp-{filename}")
            file.save(os.path.join('./', f"tmptmp-{filename}"))
            file_paths.append(f"tmptmp-{filename}")
        except Exception as e:
            logger.exception(f"Error processing file {file.filename}: {str(e)}")
            pass
    return file_paths


if __name__ == '__main__':
    app.run(debug=True)