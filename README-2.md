# Video to GIFs Project

This project allows you to upload videos, transcribe them using Whisper, and generate GIFs with synchronized text.

![Example GIF](example.gif)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Summary of Commands](#summary-of-commands)
- [API Documentation](#api-documentation)
  - [Upload Video](#upload-video)
  - [Get Video Processing Status](#get-video-processing-status)
  - [Get GIF Generation Status](#get-gif-generation-status)
  - [Get Processed Text](#get-processed-text)
  - [Generate GIFs](#generate-gifs)
  - [Get GIFs](#get-gifs)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- **Python 3.7+**: Ensure Python is installed.
- **Redis**: Required for Celery task queue. [Install Redis](https://redis.io/download).
- **Node.js and npm**: Required for the frontend. [Install Node.js and npm](https://nodejs.org/).
- **ImageMagick**: Required for text rendering in GIFs by MoviePy. [Install ImageMagick](https://imagemagick.org/script/download.php).

## Installation

### Backend

1. **Clone the Repository**

   Clone the repository and navigate to the backend directory:
   ```bash
   git clone https://github.com/anjalilaishram/video-to-gifs.git
   cd video-to-gifs/backend
   ```

2. **Create and Activate Virtual Environment**

   Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Python Dependencies**

   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ImageMagick**

   Install ImageMagick, needed by MoviePy for text rendering in GIFs:
   - **macOS**: Use Homebrew:
     ```bash
     brew install imagemagick
     ```
   - **Ubuntu/Debian**: Use apt:
     ```bash
     sudo apt update
     sudo apt install imagemagick
     ```
   - **Windows**: Download and install ImageMagick from the [official website](https://imagemagick.org/script/download.php). During installation, make sure to check the option to add ImageMagick to your system PATH.

5. **Configure Environment Variables**

   Create a `.env` file in the `backend` directory with the following content:
   ```
   MONGO_URI=mongodb://localhost:27017/video_processing_db
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

6. **Run Redis**

   Ensure Redis is running. Start Redis with:
   ```bash
   redis-server
   ```

7. **Run MongoDB**

   Ensure MongoDB is running. Start MongoDB with:
   ```bash
   sudo systemctl start mongod
   ```

8. **Run Flask Application**

   Run the Flask application:
   ```bash
   python app.py
   ```

9. **Run Celery Worker**

   In a new terminal, navigate to the backend directory and start the Celery worker:
   ```bash
   celery -A celery_worker.celery worker --loglevel=info
   ```

### Frontend

1. **Navigate to the Frontend Directory**

   Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. **Install Node.js Dependencies**

   Install the required Node.js packages:
   ```bash
   npm install
   ```

3. **Start the React Development Server**

   Start the React development server:
   ```bash
   npm start
   ```
   The frontend will be running at `http://localhost:3000`.

## Configuration

Configure the backend using the `.env` file located in the `backend` directory. Set the appropriate environment variables for MongoDB, Redis, and other settings.

## Running the Project

1. **Backend**: Follow the backend installation steps to run the Flask server and Celery worker.
2. **Frontend**: Follow the frontend installation steps to run the React development server.

## Summary of Commands

### Backend Commands

- **Clone the repository and navigate to backend directory**:
  ```bash
  git clone https://github.com/anjalilaishram/video-to-gifs.git
  cd video-to-gifs/backend
  ```

- **Create and activate a virtual environment**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Install dependencies**:
  ```bash
  pip install -r requirements.txt
  ```

- **Start Redis**:
  ```bash
  redis-server
  ```

- **Start MongoDB**:
  ```bash
  sudo systemctl start mongod
  ```

- **Run the Flask app**:
  ```bash
  python app.py
  ```

- **Run the Celery worker**:
  ```bash
  celery -A celery_worker.celery worker --loglevel=info
  ```

### Frontend Commands

- **Navigate to the frontend directory**:
  ```bash
  cd ../frontend
  ```

- **Install dependencies**:
  ```bash
  npm install
  ```

- **Start the React development server**:
  ```bash
  npm start
  ```

## API Documentation

### Upload Video

**Endpoint**: `POST /upload`

- **Description**: Uploads a video file for processing.
- **Request**:
  - **Headers**: `Content-Type: multipart/form-data`
  - **Body**: Form-data containing the video file.

  | Key  | Type | Description        |
  |------|------|--------------------|
  | file | File | The video file to upload |

- **Response**:
  - **Success (200 OK)**
    ```python
    {
      "video_id": "string",
      "task_id": "string"
    }
    ```

    | Key       | Type   | Description                   |
    |-----------|--------|-------------------------------|
    | video_id  | string | The unique ID for the uploaded video |
    | task_id   | string | The Celery task ID for processing the video |

  - **Error (400 Bad Request)**
    ```python
    {
      "error": "No file part" | "No selected file"
    }
    ```

### Get Video Processing Status

**Endpoint**: `GET /status/video/{task_id}`

- **Description**: Gets the processing status of the uploaded video.
- **Request**:
  - **Path Parameters**:

    | Parameter | Type   | Description               |
    |-----------|--------|---------------------------|
    | task_id   | string | The Celery task ID for video processing |

- **Response**:
  - **Success (200 OK)**
    ```python
    {
      "status": "queued" | "processing" | "processed" | "failed",
      "queue_position": integer | null,
      "task_status": "PENDING" | "STARTED" | "SUCCESS" | "FAILURE" | "REVOKED",
      "video_id": "string"
    }
    ```

    | Key            | Type    | Description                                       |
    |----------------|---------|---------------------------------------------------|
    | status         | string  | The current processing status of the video        |
    | queue_position | integer | Position in the processing queue, or null         |
    | task_status    | string  | The Celery task status                            |
    | video_id       | string  | The unique ID of the video                        |

  - **Error (404 Not Found)**
    ```python
    {
      "error": "Task not found"
    }
    ```

### Get GIF Generation Status

**Endpoint**: `GET /status/gif/{task_id}`

- **Description**: Gets the status of GIF generation for the video.
- **Request**:
  - **Path Parameters**:

    | Parameter | Type   | Description               |
    |-----------|--------|---------------------------|
    | task_id   | string | The Celery task ID for GIF generation |

- **Response**:
  - **Success (200 OK)**
    ```python
    {
      "status": "queued" | "processing" | "complete" | "failed",
      "queue_position": integer | null,
      "task_status": "PENDING" | "STARTED" | "SUCCESS" | "FAILURE" | "REVOKED",
      "video_id": "string"
    }
    ```

    | Key            | Type    | Description                                       |
    |----------------|---------|---------------------------------------------------|
    | status         | string  | The current status of the GIF generation          |
    | queue_position | integer | Position in the generation queue, or null         |
    | task_status    | string  | The Celery task status                            |
    | video_id       | string  | The unique ID of the video                        |

  - **Error (404 Not Found)**
    ```python
    {
      "error": "Task not found"
    }
    ```

### Get Processed Text

**Endpoint**: `

GET /result/{video_id}`

- **Description**: Gets the transcribed text segments from the video.
- **Request**:
  - **Path Parameters**:

    | Parameter | Type   | Description               |
    |-----------|--------|---------------------------|
    | video_id  | string | The unique ID of the video |

- **Response**:
  - **Success (200 OK)**
    ```python
    [
      {
        "segment_start": float,
        "segment_end": float,
        "text": "string",
        "words": [
          {
            "start_time": float,
            "end_time": float,
            "word": "string"
          }
        ]
      }
    ]
    ```

    | Key            | Type   | Description                                         |
    |----------------|--------|-----------------------------------------------------|
    | segment_start  | float  | Start time of the segment in seconds                |
    | segment_end    | float  | End time of the segment in seconds                  |
    | text           | string | Full text of the segment                            |
    | words          | array  | List of words with individual timestamps            |

  - **Error (404 Not Found)**
    ```python
    {
      "text_segments": []
    }
    ```

### Generate GIFs

**Endpoint**: `POST /generate_gifs`

- **Description**: Generates GIFs based on the processed text segments of the video.
- **Request**:
  - **Headers**: `Content-Type: application/json`
  - **Body**:
    ```python
    {
      "video_id": "string",
      "segments_list": [
        {
          "segment_start": float,
          "segment_end": float,
          "text": "string",
          "words": [
            {
              "start_time": float,
              "end_time": float,
              "word": "string"
            }
          ]
        }
      ],
      "template": {
        "font_color": "string",
        "font_size": integer,
        "position": "string",
        "max_words": integer,
        "fps": integer
      }
    }
    ```

    | Key            | Type     | Description                                         |
    |----------------|----------|-----------------------------------------------------|
    | video_id       | string   | The unique ID of the video                          |
    | segments_list  | array    | List of segments with text                          |
    | segment_start  | float    | Start time of the segment in seconds                |
    | segment_end    | float    | End time of the segment in seconds                  |
    | text           | string   | Full text of the segment                            |
    | words          | array    | List of words with individual timestamps            |
    | template       | object   | Template settings for GIF generation                |
    | font_color     | string   | Font color of the text                              |
    | font_size      | integer  | Font size of the text                               |
    | position       | string   | Position of the text (`'top_left'`, `'top_center'`, `'top_right'`, `'center_left'`, `'center'`, `'center_right'`, `'bottom_left'`, `'bottom_center'`, `'bottom_right'`) |
    | max_words      | integer  | Maximum words to show at once                       |
    | fps            | integer  | Frames per second for the GIF                       |

- **Response**:
  - **Success (200 OK)**
    ```python
    {
      "status": "queued",
      "task_id": "string"
    }
    ```

    | Key    | Type   | Description                            |
    |--------|--------|----------------------------------------|
    | status | string | Indicates the task is queued for GIF generation |
    | task_id| string | The Celery task ID for GIF generation |

  - **Error (400 Bad Request)**
    ```python
    {
      "error": "Segments list not provided and not found in the database"
    }
    ```

### Get GIFs

**Endpoint**: `GET /gifs/{video_id}`

- **Description**: Downloads the generated GIFs as a ZIP file.
- **Request**:
  - **Path Parameters**:

    | Parameter | Type   | Description               |
    |-----------|--------|---------------------------|
    | video_id  | string | The unique ID of the video |

- **Response**:
  - **Success (200 OK)**

    The response will be a ZIP file containing the generated GIFs.

  - **Error (404 Not Found)**
    ```python
    {
      "error": "GIFs not ready or failed"
    }
    ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.