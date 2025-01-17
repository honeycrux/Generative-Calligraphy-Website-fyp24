from flask import Flask, request, send_from_directory, abort, send_file, render_template
from flask_cors import CORS
from flask import jsonify, Response
from werkzeug.exceptions import HTTPException
import shutil
import os, subprocess
import datetime
import sys
from PIL import Image

### Settings

# Directory of the backend files
BACKEND_DIRECTORY = './back-end/'

# Directory where result files are stored
FILES_DIRECTORY = './back-end/'

### Functions and Classes

class ServerConfig:
    backend_directory: str
    files_directory: str
    outputs_directory: str

    def __init__(self, backend_directory: str, files_directory: str):
        self.backend_directory = backend_directory.rstrip('/')
        self.files_directory = files_directory.rstrip('/')
        self.outputs_directory = 'outputs'

    def get_output_directory(self):
        return f'{self.files_directory}/{self.outputs_directory}'

    def get_session_directory(self, session_id: str):
        return f'{self.files_directory}/{self.outputs_directory}/{session_id}'

    def get_result_directory(self, session_id: str):
        return f'{self.files_directory}/{self.outputs_directory}/{session_id}/result_web'

    def get_content_directory(self, session_id: str):
        return f'{self.files_directory}/{self.outputs_directory}/{session_id}/content_folder'

    # Experimental: Ensure file permissions
    def ensure_file_permission(self, session_id: str):
        os.chmod(self.get_output_directory(), 0o777)
        for root, dirs, files in os.walk(f'{self.files_directory}/{self.outputs_directory}/{session_id}'):
            for dir in dirs:
                os.chmod(os.path.join(root, dir), 0o777)
            for file in files:
                os.chmod(os.path.join(root, file), 0o777)

def run_command(command):
        """
        Executes a shell command and returns its output.

        Args:
            command (str): The command to be executed.

        Returns:
            str: The output of the command if successful, or an error message if the command fails.
        """

        try:
            result = subprocess.check_output(command, shell=True, text=True, encoding='utf-8')
            print(result)
            return result, True
        except subprocess.CalledProcessError as e:
            return f'Error: {e.output}', False

### Flask App

app = Flask(__name__)
CORS(app)
server_config = ServerConfig(BACKEND_DIRECTORY, FILES_DIRECTORY)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#### Step 1: Save Files - Frontend requests to save two files to the server: char-input.txt and nonCH-char-input.txt

@app.route('/save-file', methods=['GET'])
def save_file():
    try:
        # Get the content and filename from the request
        filename = request.args.get('filename')
        content = request.args.get('content')

        # Get the SESSION ID from the request
        session_id = request.args.get('session_id')

        # Check if the content, filename, and SESSION_ID are provided
        if filename is None or content is None or session_id is None:
            abort(400, description="Invalid request parameters")

        # Save the file
        output_directory = server_config.get_output_directory()
        session_directory = server_config.get_session_directory(session_id)
        os.makedirs(session_directory, exist_ok=True)  # Create parent directories if needed
        os.chmod(output_directory, 0o777)
        os.chmod(session_directory, 0o777)
        file_path = os.path.join(session_directory, filename)

        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(content)

        # Change permissions of the file
        os.chmod(file_path, 0o777)

        return 'File saved successfully.', 200
    except HTTPException as e:
        raise e
    except Exception as e:
        abort(500, description=str(e))

#### Step 2: Font2Img - Frontend requests to generate images from characters in either char-input.txt or nonCH-char-input.txt

@app.route('/font2img', methods=['GET'])
def font2img():
    try: 
        # Get the SESSION ID from the request
        session_id = request.args.get('session_id')

        if not session_id:
            abort(400, description="Invalid request parameters")

        isCH = ( request.args.get('isCH') == '1' )

        backend_directory = server_config.backend_directory
        session_directory = server_config.get_session_directory(session_id)
        content_directory = server_config.get_content_directory(session_id)
        result_directory = server_config.get_result_directory(session_id)

        if not os.path.exists(content_directory):
            os.mkdir(content_directory) 

        character_file = 'char-input.txt' if isCH else 'nonCH-char-input.txt'
        # If isCH, save to content_folder to generate images; otherwise, save to result_web for direct display
        save_path = content_directory if isCH else result_directory

        command = (
            f'python {backend_directory}/font2img.py '
            f'--ttf_path {backend_directory}/ttf_folder '
            f'--save_path {save_path} '
            f'--chara {session_directory}/{character_file}'
        )

        result, success = run_command(command)

        if not success:
            abort(500, description=result)

        # result = subprocess.check_output(command, shell=True)
        # result = os.popen(command).read()
        return f'Command "{command}" executed'
    except HTTPException as e:
        raise e
    except Exception as e:
        abort(500, description=str(e))

#### Step 3: Generate Images - Frontend requests to generate images from the provided characters

@app.route('/generate_result', methods=['GET'])
def generate_result():
    try:
        # Get the SESSION ID from the request
        session_id = request.args.get('session_id')

        if not session_id:
            abort(400, description="Invalid request parameters")

        backend_directory = server_config.backend_directory
        content_directory = server_config.get_content_directory(session_id)
        result_directory = server_config.get_result_directory(session_id)

        content_directory_is_empty = len(os.listdir(content_directory)) == 0

        if content_directory_is_empty:
            return f"No characters to sample from."

        command = (
            f'mpiexec -n 1 python {backend_directory}/sample.py '
            f'--cfg_path "{backend_directory}/cfg/test_cfg.yaml" '
            f'--session_id "{session_id}" '
            f'--model_path "{backend_directory}/ckpt/ema_0.9999_446000.pt" '
            f'--sty_img_path "{backend_directory}/lan.png" '
            f'--con_folder_path "{content_directory}" '
            f'--total_txt_file "{backend_directory}/wordlist.txt" '
            f'--img_save_path "{result_directory}"'
        )

        result, success = run_command(command)

        if not success:
            abort(500, description=result)

        return f'Command "{command}" executed'
    except HTTPException as e:
        raise e
    except Exception as e:
        abort(500, description=str(e))

### [Unused] For Merging Images

@app.route('/merge_img', methods=['GET'])
def merge_img():
    try:
        # Get the SESSION ID from the request
        session_id = request.args.get('session_id')
        if not session_id:
            abort(400, description="Invalid request parameters")
        result_directory = server_config.get_result_directory(session_id)

        # Check if the directory exists
        if not os.path.exists(result_directory):
            abort(404, description="directory not found")

        new_image_name = ''
        imagePaths = []
        for file in os.listdir(result_directory):
            # Check if the file exists
            if not os.path.isfile(os.path.join(result_directory, file)):
                abort(404, description="Result file not found")

            new_image_name = new_image_name + file[0]
            imgPath = result_directory + file
            imagePaths.append(imgPath)

        # Return directly if there is only one image
        if len(imagePaths) == 1:
            response = new_image_name + '.png'
            return Response(response, mimetype='text/plain')

        # Start merging images
        images = [Image.open(path) for path in imagePaths]
        widths, heights = zip(*(i.size for i in images))

        total_img_width = sum(widths)
        max_img_height = max(heights)

        new_img = Image.new('RGB', (total_img_width, max_img_height))

        x_offset = 0
        for img in images:
            new_img.paste(img, (x_offset,0))
            x_offset += img.size[0]

        new_img_path = result_directory + new_image_name + '.png'
        new_img.save(new_img_path)

        response = new_image_name + '.png'
        return Response(response, mimetype='text/plain')

    except HTTPException as e:
        raise e
    except Exception as e:
        abort(500, description=str(e))

### [Unused] For Retrieving Files

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    files_directory = server_config.files_directory
    try:
        # Check if the file exists in the directory
        if not os.path.isfile(os.path.join(files_directory, filename)):
            abort(404, description="File not found")
        # Send the file to the client
        return send_from_directory(files_directory, filename)
    except HTTPException as e:
        raise e
    except Exception as e:
        abort(500, description=str(e))

# [Unused] For Retrieving Result Files from Result Directory

@app.route('/return_paths', methods=['GET'])
def return_result_paths():
    # Get the SESSION ID from the request
    session_id = request.args.get('session_id')
    if not session_id:
        abort(400, description="Invalid request parameters")
    result_directory = server_config.get_result_directory(session_id)

    return_paths = []
    return_file_names = []
    try:
        # Check if the directory exists
        if not os.path.exists(result_directory):
            abort(404, description="directory not found")

        for file in os.listdir(result_directory):
            # Check if the file exists
            if not os.path.isfile(os.path.join(result_directory, file)):
                abort(404, description="Result file not found")
            return_paths.append(os.path.join(result_directory, file))
            return_file_names.append(file)
        
        return send_from_directory(result_directory, return_file_names[0])
        # Send the file paths back to the client
        # return jsonify(return_paths)
    except HTTPException as e:
        raise e
    except Exception as e:
        abort(500, description=str(e))

### Step 4: Retrieve Image Files from Result Directory

@app.route('/get_images', methods=['GET'])
def get_images():
    try:
        # Get the SESSION ID from the request
        session_id = request.args.get('session_id')
        if not session_id:
            abort(400, description="Invalid request parameters")
        result_directory = server_config.get_result_directory(session_id)

        # Check if the directory exists
        if not os.path.exists(result_directory):
            abort(404, description="Directory not found")

        images = []
        for file in os.listdir(result_directory):
            # Check if the file exists
            if not os.path.isfile(os.path.join(result_directory, file)):
                abort(404, description="Result file not found")
            images.append({'image_name': file})

        return jsonify(images)
    except HTTPException as e:
        raise e
    except Exception as e:
        abort(500, description=str(e))

### Step 5: Serve Image Files

@app.route('/image/<path:session_id>/<path:filename>')
def serve_image(session_id: str, filename: str):
    result_directory = server_config.get_result_directory(session_id)
    content_directory = server_config.get_content_directory(session_id)
    if ( not os.path.exists(result_directory) ) or ( not os.path.exists(content_directory) ):
        abort(404, description="Directory not found")

    if os.path.isfile(os.path.join(result_directory, filename)):
        directory = result_directory 
    elif os.path.isfile(os.path.join(content_directory, filename)):
        directory = content_directory 
    else:
        abort(404, description="Result file not found")

    # directory = res_files_directory 
    return send_from_directory(directory, filename)

# Step 0: Clear Directory - Frontend requests to clear the specified directory

@app.route('/clear_dir')
def clear_dir():
    try:
        # Get the SESSION ID from the request
        session_id = request.args.get('session_id')
        if not session_id:
            abort(400, description="Invalid request parameters")
        session_directory = server_config.get_session_directory(session_id)

        # Check if the directory exists
        if not os.path.exists(session_directory):
            abort(404, description="directory not found")

        # Remove all files and subdirectories within the directory
        shutil.rmtree(session_directory)

        return f"The directory '{session_directory}' has been successfully deleted."

    except HTTPException as e:
        raise e
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6700, debug=True)
