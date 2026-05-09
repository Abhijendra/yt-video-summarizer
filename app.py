from flask import Flask
import os 
from log_config import setup_logging
from services.youtube_service import *
from flask import request, jsonify, render_template
from werkzeug.exceptions import BadRequest, InternalServerError

# import logging 

setup_logging()

from dotenv import load_dotenv
load_dotenv(override=True)

from services.summarizer import Summarizer

# ======================================================
#            FLASK APP CONFIGURATION
# ======================================================

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# ======================================================
#            HELPERS
# ======================================================

def summarize(video_id:str):
    logger.info(f"Started summarizing video. video Id: {video_id}")
    
    video_transcript = get_ytvideo_transcript(video_id=video_id)
    logger.info(f"Fetched video transcript.")

    summarizer = Summarizer()
    summarizer.set_transcript(transcript= video_transcript)

    video_summary = summarizer.summarize()
    logger.info(f"Summarization completed.")

    return video_summary


# ======================================================
#            FLASK ROUTES
# ======================================================

@app.route("/health", methods=["GET"])
def health_check():
    logging.info("Recieved hit at health check endpoint.")
    return {"status":"healthy"}

@app.route("/fetch", methods=["POST"])
def fetch_link():
    try:
        raw_user_input = request.get_data()
        
        if not raw_user_input:
            raise BadRequest("Empty request body")
        
        logger.info(f"Recieved Raw User input: {raw_user_input}")
        video_link = raw_user_input.decode("utf-8")  # str

        if not video_link:
            raise BadRequest("Video link cannot be empty.")

        logger.info(f"Video Link: {video_link}")
        
        try:
            vid = get_video_id_from_link(video_link=video_link)
        
        except Exception as e:
            logger.exception(f"Failed to extract video id.")
            raise BadRequest("Invalid Youtube video link.")
        
        logger.info(f"Recieved Video Id: {vid}")

        try:
            generated_summary = summarize(video_id=vid)
        except Exception as e:
            logger.exception("Summarization failed.")
            raise InternalServerError("Failed to generate summary.")

        return jsonify({
            "status": "success",
            "video_id": vid,
            "generated_summary": generated_summary
        }), 200
        
    except BadRequest as e:
        logger.warning(f"Client error: {e.description}")
        return jsonify({
            "status": "error",
            "message": e.description
        }), 400
    
    except InternalServerError as e:
        logger.exception(f"Server error: {e.description}")
        return jsonify({
            "status": "error",
            "message": e.description
        }), 500

    except Exception as e:
        # Catch-all safeguard
        logger.exception("Unexpected error occurred")
        return jsonify({
            "status": "error",
            "message": "Unexpected server error"
        }), 500        
    
    
# def answer_query():
#     return 
@app.route("/")
def home():
    return render_template("index.html")

# ======================================================
#            MAIN
# ======================================================

if __name__ == '__main__':
    logger.info("YouTube Video Summarizer application starting...")
    app.run(debug=True, host='0.0.0.0', port=5000)