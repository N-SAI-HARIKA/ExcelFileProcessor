from flask import Flask, request, send_file, render_template
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set up folder for file uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xlsx'}

# Check if the uploaded file is an Excel file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Process the Excel file and perform the necessary operations
def process_excel(file_path):
    # Load the data from the file
    data = pd.read_excel(file_path, sheet_name='Form responses 1')

    # Select and rename the columns (strip whitespace from column names)
    data.columns = data.columns.str.strip()  # Removes trailing and leading spaces
    formatted_data = data[['Full name', 'Registration No.', 'Department']]
    formatted_data.columns = ['Name', 'Registration No.', 'Department']

    # Format the output with double quotes
    formatted_data['Formatted Output'] = formatted_data.apply(
        lambda row: f'"{row["Name"]}", "{row["Registration No."]}", "{row["Department"]}"',
        axis=1
    )

    # Save the formatted output to a new spreadsheet
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'formatted_output.xlsx')
    formatted_data[['Formatted Output']].to_excel(output_path, index=False, header=False)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            # Save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the file and get the updated file path
            updated_file_path = process_excel(file_path)

            # Provide the download link for the updated file
            return render_template('download.html', file_path=updated_file_path)
    return render_template('upload.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    # Create the uploads folder if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    app.run(debug=True)
