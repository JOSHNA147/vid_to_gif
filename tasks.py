from celery_worker import celery
from utils import transcribe_video, generate_gif_zip
from models import update_video_status, update_gif_status, remove_from_queue
from config import Config
import os
import traceback

@celery.task(name='tasks.process_video_task')
def process_video_task(video_id, video_path):
    task_id = process_video_task.request.id
    try:
        text_segments = transcribe_video(video_path)  # Replace with actual Whisper AI call
        update_video_status(task_id, 'processed', text_segments)
    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        traceback.print_exc()  # Log the entire traceback
        update_video_status(task_id, 'failed')
    finally:
        remove_from_queue('process_video', task_id)

@celery.task(name='tasks.generate_gifs_task')
def generate_gifs_task(video_id, segments_list, template):
    task_id = generate_gifs_task.request.id
    try:
        gif_zip_path = os.path.join(Config.GIF_FOLDER, f"{video_id}.zip")
        generate_gif_zip(video_id, segments_list, template, gif_zip_path)
        update_gif_status(task_id, 'complete')
    except Exception as e:
        print(f"Error generating GIFs for video {video_id}: {e}")
        traceback.print_exc()  # Log the entire traceback
        update_gif_status(video_id, 'failed')
    finally:
        remove_from_queue('generate_gifs', task_id)
