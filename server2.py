from flask import Flask, request, send_from_directory, abort, send_file, render_template
from flask_cors import CORS
from flask import jsonify, Response
import shutil
import os, subprocess
import datetime
import sys
from PIL import Image

app = Flask(__name__)
CORS(app)

FILES_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff_summer/'
# Directory where result files are stored
# RES_FILES_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff_summer/result_web'
# RES_FILES_DIRECTORY = '/result_web'


SESSION_ID = '01'
SESSION_PATH = '01/'

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# Directory where txt files are stored
SAVE_DIRECTORY = '/research/d2/fyp23/lylee0/Font-diff_summer/'

@app.route('/save-file', methods=['GET'])
def save_file():
    try:
        # Get the content and filename from the request
        filename = request.args.get('filename')
        content = request.args.get('content')

        # Get the SESSION ID from the request
        SESSION_ID = request.args.get('session_id')
        SESSION_PATH = SESSION_ID + '/'

        # Check if the content and filename are provided
        if not filename:
            abort(400, description="Invalid request parameters")

        # Save the file
        SESSION_DIRECTORY = SAVE_DIRECTORY + SESSION_PATH
        os.makedirs(SESSION_DIRECTORY, exist_ok=True)  # Create parent directories if needed
        file_path = os.path.join(SESSION_DIRECTORY, filename)

        with open(file_path, 'w') as file:
            file.write(content)

        # Change permissions of the file
        os.chmod(file_path, 0o777)

        return 'File saved successfully.', 200
    except Exception as e:
        abort(500, description=str(e))

@app.route('/font2img', methods=['GET'])
def font2img():
    try: 
        # Get the SESSION ID from the request
        SESSION_ID = request.args.get('session_id')
        SESSION_PATH = SESSION_ID + '/'

        isCH = ( request.args.get('isCH') == '1' )

        CONTENT_DIRECTORY = SAVE_DIRECTORY + SESSION_PATH + 'content_folder/'
        if not os.path.exists(CONTENT_DIRECTORY):
            os.mkdir(CONTENT_DIRECTORY) 
        if isCH:
            command = f'python /research/d2/fyp23/lylee0/Font-diff_summer/font2img.py --save_path ./{SESSION_ID}/content_folder --chara ./{SESSION_ID}/char-input.txt'  # Shell command to be executed
        else: 
            command = f'python /research/d2/fyp23/lylee0/Font-diff_summer/font2img.py --save_path ./{SESSION_ID}/content_folder --chara ./{SESSION_ID}/nonCH-char-input.txt'  # Shell command to be executed
        # command = f'mpiexec -n 1 python sample.py --cfg_path cfg/test_cfg.yaml'

        result = run_command(command)
        # result = subprocess.check_output(command, shell=True)
        # result = os.popen(command).read()
        return f'Command "{command}" executed'
    except Exception as e:
        return str(e)

@app.route('/generate_result', methods=['GET'])
def generate_result():
    try:
        # Get the SESSION ID from the request
        SESSION_ID = request.args.get('session_id')
        SESSION_PATH = SESSION_ID + '/'
        
        command = f'mpiexec -n 1 python sample.py --cfg_path cfg/test_cfg.yaml --session_id {SESSION_ID}'
        # command = f'mpiexec -n 1 python sample_backup.py --cfg_path cfg/test_cfg.yaml'
 
        result = run_command(command)
        return f'Command "{command}" executed'
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


@app.route('/get_images', methods=['GET'])
def get_images():
    try:
        # Get the SESSION ID from the request
        session_id = request.args.get('session_id')
        session_path = session_id + '/'
        res_files_directory = FILES_DIRECTORY + session_path + 'result_web/'

        # Check if the directory exists
        if not os.path.exists(res_files_directory):
            abort(404, description="Directory not found")

        images = []
        for file in os.listdir(res_files_directory):
            # Check if the file exists
            if not os.path.isfile(os.path.join(res_files_directory, file)):
                abort(404, description="Result file not found")
            images.append({'image_name': file})

        return jsonify(images)
    except Exception as e:
        abort(500, description=str(e))


@app.route('/image/<path:session_id>/<path:filename>')
def serve_image(session_id, filename):
    session_path = session_id + '/'
    res_files_directory = FILES_DIRECTORY + session_path + 'result_web/'
    content_files_directory = FILES_DIRECTORY + session_path + 'content_folder/'
    if ( not os.path.exists(res_files_directory) ) or ( not os.path.exists(content_files_directory) ):
        abort(404, description="Directory not found")
    
    if os.path.isfile(os.path.join(res_files_directory, filename)):
        directory = res_files_directory 
    elif os.path.isfile(os.path.join(content_files_directory, filename)):
        directory = content_files_directory 
    else:
        abort(404, description="Result file not found")

    # directory = res_files_directory 
    return send_from_directory(directory, filename)


@app.route('/merge_img', methods=['GET'])
def merge_img():
    try:
        # Get the SESSION ID from the request
        SESSION_ID = request.args.get('session_id')
        SESSION_PATH = SESSION_ID + '/'
        TARGET_DIRECTORY = FILES_DIRECTORY + SESSION_PATH + 'result_web/'

        # Check if the directory exists
        if not os.path.exists(TARGET_DIRECTORY):
            abort(404, description="directory not found")

        new_image_name = ''
        imagePaths = []
        for file in os.listdir(TARGET_DIRECTORY):
            # Check if the file exists
            if not os.path.isfile(os.path.join(TARGET_DIRECTORY, file)):
                abort(404, description="Result file not found")

            new_image_name = new_image_name + file[0]
            imgPath = TARGET_DIRECTORY + file
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

        new_img_path = TARGET_DIRECTORY + new_image_name + '.png'
        new_img.save(new_img_path)

        response = new_image_name + '.png'
        return Response(response, mimetype='text/plain')

    except Exception as e:
        abort(500, description=str(e))


@app.route('/clear_dir')
def clear_dir():
    try:
        # Get the SESSION ID from the request
        SESSION_ID = request.args.get('session_id')
        SESSION_PATH = SESSION_ID + '/'
        TARGET_DIRECTORY = FILES_DIRECTORY + SESSION_PATH 

        # Check if the directory exists
        if not os.path.exists(TARGET_DIRECTORY):
            abort(404, description="directory not found")

        # Remove all files and subdirectories within the directory
        shutil.rmtree(TARGET_DIRECTORY)

        return f"The directory '{TARGET_DIRECTORY}' has been successfully deleted."

    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)

