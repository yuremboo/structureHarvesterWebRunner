import os
import zipfile
import shutil
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

# Paths to folders
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

# Folder settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Main page
@app.route('/')
def upload_form():
    return render_template('index.html')

# Handling file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # Save the uploaded archive
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Extract the archive
    extract_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted')
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    # Find the folder created after extraction
    extracted_subfolders = [f for f in os.listdir(extract_folder) if os.path.isdir(os.path.join(extract_folder, f))]
    if len(extracted_subfolders) == 1:
        extracted_folder_path = os.path.join(extract_folder, extracted_subfolders[0])
    else:
        return 'Unexpected archive structure. Expected a single folder inside.'

    # Create the result folder
    result_folder = os.path.join(app.config['RESULT_FOLDER'], 'result')
    os.makedirs(result_folder, exist_ok=True)

    # Run the command: structureHarvester.py --dir=extracted_folder_path --out=result
    subprocess.run(['python', 'structureHarvester.py', '--dir', extracted_folder_path, '--out', result_folder])

    # Clean up extracted folder
    shutil.rmtree(extract_folder)

    # Archive the result
    result_zip = os.path.join(app.config['RESULT_FOLDER'], 'result.zip')
    shutil.make_archive(result_zip.replace('.zip', ''), 'zip', result_folder)

    # Return the result archive for download
    return send_file(result_zip, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
