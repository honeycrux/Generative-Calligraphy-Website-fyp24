from flask import Flask, send_from_directory, abort, send_file, render_template
import os

app = Flask(__name__)

# Directory where files are stored
FILES_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff_content/'
# FILES_DIRECTORY = '/Users/heiwan/desktop/'

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
      

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)