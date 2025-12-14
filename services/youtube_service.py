from youtube_transcript_api import YouTubeTranscriptApi

import logging

logger = logging.getLogger(__name__)

def get_video_id_from_link(video_link:str):
    video_id = None 
    try:
        video_id = video_link.split("?v=")[1]
    except Exception as e:
        logger.info(f"Not a valid YouTube video link.")
        
    return video_id 

def get_ytvideo_transcript(video_id:str):

    try:
        youtube_api = YouTubeTranscriptApi()
        fetched_transcript = youtube_api.fetch(video_id, preserve_formatting=True)
        transcript = ' '.join(snippet.text for snippet in fetched_transcript.snippets)
        return transcript

    except Exception as e:
        # return 'No captions available for this video'
        return "" 

if __name__  == "__main__":

    # video_id = get_video_id_from_link(video_link)
    video_link = "https://www.youtube.com/watch?v=JTJPMJW9JZU"
    video_id = "JTJPMJW9JZU"
    # transcript = get_ytvideo_transcript(video_id=video_id)
    # if len(transcript):
    #     print(len(transcript))
    logger.info(video_link.split("?v=")[1]) 
