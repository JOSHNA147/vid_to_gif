from pymongo import MongoClient
from config import Config
import redis

client = MongoClient(Config.MONGO_URI)
db = client['video_processing_db']
redis_client = redis.StrictRedis.from_url(Config.CELERY_BROKER_URL)

def save_video_info(video_id, status, task_id=None):
    db.videos.insert_one({
        'video_id': video_id,
        'status': status,
        'text_segments': [],
        'task_id': task_id
    })

def update_video_status(task_id, status, text_segments=None):
    update = {'status': status}
    if text_segments is not None:
        update['text_segments'] = text_segments
    db.videos.update_one({'task_id': task_id}, {'$set': update})


def get_video_status(video_id):
    """
    Retrieve the status of video processing from the database.
    
    Args:
        video_id (str): The unique ID of the video.
    
    Returns:
        dict: The status information of the video.
    """
    return db.videos.find_one({"video_id": video_id}, {"_id": 0, "task_id": 1, "status": 1})

def get_gif_status(video_id):
    """
    Retrieve the status of GIF generation from the database.
    
    Args:
        video_id (str): The unique ID of the video.
    
    Returns:
        dict: The status information of the GIF generation.
    """
    return db.gifs.find_one({"video_id": video_id}, {"_id": 0, "task_id": 1, "status": 1})

def get_position_in_queue(queue_name, task_id):
    """
    Retrieve the position of a task in the queue.
    
    Args:
        queue_name (str): The name of the queue.
        task_id (str): The task ID.
    
    Returns:
        int: The position in the queue or None if not found.
    """
    # Simplified example. Actual implementation might vary based on your queue monitoring setup.
    tasks = list(db.celery_tasks.find({"queue": queue_name}).sort("date_created"))
    task_ids = [task["task_id"] for task in tasks]
    if task_id in task_ids:
        return task_ids.index(task_id) + 1
    return None

def get_video_status_by_task(task_id):
    return db.videos.find_one({"task_id": task_id}, {"_id": 0, "video_id": 1, "status": 1})

def get_gif_status_by_task(task_id):
    return db.gifs.find_one({"task_id": task_id}, {"_id": 0, "video_id": 1, "status": 1})


def get_processed_text(video_id):
    video = db.videos.find_one({'video_id': video_id})
    if video:
        return {'text_segments': video.get('text_segments', [])}
    return {'text_segments': []}

def save_gif_info(video_id, status, task_id=None):
    db.gifs.insert_one({
        'video_id': video_id,
        'status': status,
        'task_id': task_id
    })

def update_gif_status(task_id, status):
    db.gifs.update_one({'task_id': task_id}, {'$set': {'status': status}})

def get_gif_info(video_id):
    gif = db.gifs.find_one({'video_id': video_id})
    if gif:
        task_id = gif.get('task_id')
        return {'status': gif.get('status', 'unknown'), 'task_id': task_id}
    return {'status': 'not found'}

def add_to_queue(task_type, task_id):
    redis_client.rpush(f"{task_type}_queue", task_id)

def get_position_in_queue(task_type, task_id):
    queue = redis_client.lrange(f"{task_type}_queue", 0, -1)
    try:
        return queue.index(task_id.encode('utf-8'))
    except ValueError:
        return None

def remove_from_queue(task_type, task_id):
    redis_client.lrem(f"{task_type}_queue", 0, task_id)

def get_segments_list(video_id):
    """
    Retrieve the text_segments for the given video_id from the database.
    
    Args:
        video_id (str): The unique ID of the video.
    
    Returns:
        list: The text_segments of the video or None if not found.
    """
    video = db.videos.find_one({"video_id": video_id}, {"text_segments": 1})
    return video.get("text_segments") if video else None