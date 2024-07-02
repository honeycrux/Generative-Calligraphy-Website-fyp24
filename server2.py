from flask import Flask, request, send_from_directory, abort, send_file, render_template
from flask_cors import CORS
from flask import jsonify
import os, subprocess

app = Flask(__name__)
CORS(app)

FILES_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff_content/'
# Directory where result files are stored
RES_FILES_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff_content/result_web'

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# Directory where txt files are stored
SAVE_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff_content/'

@app.route('/save-file', methods=['GET'])
def save_file():
    try:
        # Get the content and filename from the request
        content = request.args.get('content')
        filename = request.args.get('filename')
        # print("filenames is.....", filename)

        # Check if the content and filename are provided
        if not content or not filename:
            abort(400, description="Invalid request parameters")

        # Save the file
        file_path = os.path.join(SAVE_DIRECTORY, filename)
        # print("file_path is.....", file_path)
        with open(file_path, 'w') as file:
            file.write(content)
        # print("file saved")

        # Change permissions of the file
        # os.chmod(file_path, 0o777)
        # print("file changed permit")

        return 'File saved successfully.', 200 
    except Exception as e:
        abort(500, description=str(e))

@app.route('/font2img', methods=['GET'])
def font2img():
    try:
        environment_name = '/research/d2/fyp23/lylee0/miniconda3/envs/down/bin/python3.9' 
        command = 'python /research/d2/fyp23/lylee0/Font-diff_content/font2img.py'  # Shell command to be executed
        # command = f'mpiexec -n 1 python sample.py --cfg_path cfg/test_cfg.yaml'

        result = run_command(command)
        # result = subprocess.check_output(command, shell=True)
        # result = os.popen(command).read()
        return f'Command "{command}" executed in Conda environment "{environment_name}"'
    except Exception as e:
        return str(e)

@app.route('/generate_result', methods=['GET'])
def generate_result():
    try:
        environment_name = '/research/d2/fyp23/lylee0/miniconda3/envs/down/bin/python3.9'
        command = f'mpiexec -n 1 python sample.py --cfg_path cfg/test_cfg.yaml'
        # command = f'mpiexec -n 1 python sample_backup.py --cfg_path cfg/test_cfg.yaml'
 
        result = run_command(command)
        return f'Command "{command}" executed in Conda environment "{environment_name}"'
    except Exception as e:
        return str(e)

def run_command(command):
        try:
            result = subprocess.check_output(command, shell=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            return f'Error: {e.output}'

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

@app.route('/return_paths', methods=['GET'])
def return_result_paths():
    return_paths = []
    return_file_names = []
    try:
        # Check if the directory exists
        if not os.path.exists(RES_FILES_DIRECTORY):
            abort(404, description="directory not found")

        for file in os.listdir(RES_FILES_DIRECTORY):
            # Check if the file exists
            if not os.path.isfile(os.path.join(RES_FILES_DIRECTORY, file)):
                abort(404, description="Result file not found")
            return_paths.append(os.path.join(RES_FILES_DIRECTORY, file))
            return_file_names.append(file)
        
        return send_from_directory(return_file_names[0])
        # Send the file paths back to the client
        # return jsonify(return_paths)
    except Exception as e:
        abort(500, description=str(e))

@app.route('/image/<path:filename>')
def serve_image(filename):
    directory = RES_FILES_DIRECTORY  
    return send_from_directory(directory, filename)

# Endpoint to fetch the image name or other data
@app.route('/get_image')
def get_image():
    image_names = []

    # Check if the directory exists
    if not os.path.exists(RES_FILES_DIRECTORY):
        abort(404, description="directory not found")

    for file in os.listdir(RES_FILES_DIRECTORY):
        # Check if the img exists
        if not os.path.isfile(os.path.join(RES_FILES_DIRECTORY, file)):
            abort(404, description="Result file not found")
        image_names.append(file)

    return jsonify({'image_name': image_names[0]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)

