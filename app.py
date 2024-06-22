from flask import Flask, request, jsonify, send_from_directory, url_for, abort
from werkzeug.utils import secure_filename
import os
import uuid
from models import save_video_info, get_processed_text, save_gif_info, get_gif_info, get_position_in_queue, add_to_queue, get_segments_list, get_gif_status_by_task, get_video_status_by_task
from tasks import process_video_task, generate_gifs_task
from config import Config
from flask_cors import CORS

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.GIF_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend interaction
app.config.from_object(Config)

# API to serve video files from UPLOAD_FOLDER without extension
@app.route('/static/videos/<string:video_id>', methods=['GET'])
def serve_video(video_id):
    video_filename = f"{video_id}.mp4"
    video_path = os.path.join(Config.UPLOAD_FOLDER, video_filename)

    if os.path.exists(video_path):
        return send_from_directory(Config.UPLOAD_FOLDER, video_filename)
    else:
        abort(404, description="Video not found")

# Serve GIFs directly from the static directory
@app.route('/static/gifs/<path:filename>')
def serve_gif(filename):
    return send_from_directory(Config.GIF_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        video_id = str(uuid.uuid4())
        save_path = os.path.join(Config.UPLOAD_FOLDER, f"{video_id}.mp4")
        file.save(save_path)
        
        # Create and save task, then add to queue
        task = process_video_task.apply_async(args=[video_id, save_path])
        add_to_queue('process_video', task.id)
        
        # Save initial video info with task ID
        save_video_info(video_id, 'queued', task.id)
        
        return jsonify({'video_id': video_id, 'task_id': task.id}), 200

@app.route('/status/video/<task_id>', methods=['GET'])
def video_status(task_id):
    # Retrieve video status using task_id
    status_info = get_video_status_by_task(task_id)
    
    if status_info:
        task = process_video_task.AsyncResult(task_id)
        position = get_position_in_queue('process_video', task_id)
        status_info['queue_position'] = position
        status_info['task_status'] = task.status
        return jsonify(status_info)
    else:
        return jsonify({'error': 'Task not found'}), 404

@app.route('/status/gif/<task_id>', methods=['GET'])
def gif_status(task_id):
    # Retrieve gif status using task_id
    status_info = get_gif_status_by_task(task_id)
    
    if status_info:
        task = generate_gifs_task.AsyncResult(task_id)
        position = get_position_in_queue('generate_gifs', task_id)
        status_info['queue_position'] = position
        status_info['task_status'] = task.status
        return jsonify(status_info)
    else:
        return jsonify({'error': 'Task not found'}), 404

@app.route('/result/<video_id>', methods=['GET'])
def get_result(video_id):
    result = get_processed_text(video_id)
    return jsonify(result)

@app.route('/generate_gifs', methods=['POST'])
def generate_gifs():
    data = request.json
    video_id = data.get('video_id')
    segments_list = data.get('segments_list')
    template = data.get('template')

    # If segments_list is not provided, retrieve it from the database
    if not segments_list:
        segments_list = get_segments_list(video_id)
        if not segments_list:
            return jsonify({'error': 'Segments list not provided and not found in the database'}), 400

    # Create and save task, then add to queue
    task = generate_gifs_task.apply_async(args=[video_id, segments_list, template])
    add_to_queue('generate_gifs', task.id)
    
    # Save initial gif info with task ID
    save_gif_info(video_id, 'queued', task.id)
    
    return jsonify({'status': 'queued', 'task_id': task.id}), 200

@app.route('/gifs/<video_id>', methods=['GET'])
def get_gifs(video_id):
    gif_info = get_gif_info(video_id)
    task_id = gif_info.get('task_id')

    if task_id:
        # Check task status and position
        task = generate_gifs_task.AsyncResult(task_id)
        position = get_position_in_queue('generate_gifs', task_id)
        gif_info['queue_position'] = position
        gif_info['task_status'] = task.status

    if gif_info.get('status') == 'complete':
        return send_from_directory(Config.GIF_FOLDER, f'{video_id}.zip', as_attachment=True)
    return jsonify(gif_info), 404

@app.route('/gif_urls/<video_id>', methods=['GET'])
def gif_urls(video_id):
    gifs_folder = Config.GIF_FOLDER
    video_folder = os.path.join(gifs_folder, video_id)
    if not os.path.exists(video_folder):
        return jsonify({'error': 'GIFs not found for this video ID'}), 404

    # Collect and sort filenames
    gifs = sorted(
        [url_for('serve_gif', filename=os.path.join(video_id, filename), _external=True)
        for filename in os.listdir(video_folder) if filename.endswith('.gif')]
    )

    return jsonify({'gif_urls': gifs})


if __name__ == '__main__':
    app.run(debug=True)
