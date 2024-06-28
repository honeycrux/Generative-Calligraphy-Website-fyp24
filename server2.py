from flask import Flask, request, send_from_directory, abort, send_file, render_template
from flask_cors import CORS
import os, subprocess

app = Flask(__name__)
CORS(app)

# Directory where files are stored
FILES_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff/'

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    try:
        # Check if the file exists in the directory
        if not os.path.isfile(os.path.join(FILES_DIRECTORY, filename)):
            abort(404, description="File not found")
        # Send the file to the client
        return send_from_directory(FILES_DIRECTORY, filename)
    except Exception as e:
        abort(500, description=str(e))

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# Directory where files are stored
SAVE_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff_content/'

@app.route('/save-file', methods=['GET'])
def save_file():
    try:
        # Get the content and filename from the request
        content = request.args.get('content')
        filename = request.args.get('filename')

        # Check if the content and filename are provided
        if not content or not filename:
            abort(400, description="Invalid request parameters")

        # Save the file
        file_path = os.path.join(SAVE_DIRECTORY, filename)
        with open(file_path, 'w') as file:
            file.write(content)

        # Change permissions of the file
        os.chmod(file_path, 0o777)

        return 'File saved successfully.', 200
    except Exception as e:
        abort(500, description=str(e))


@app.route('/execute_command', methods=['GET'])
def execute_command():
    try:
        command = 'hostname -I'  # Shell command to be executed
        result = os.popen(command).read()
        return result
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
