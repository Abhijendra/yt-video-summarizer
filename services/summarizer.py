import os 
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken 
from typing import List
import time
import logging
logger = logging.getLogger(__name__)


# groq = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def clean_transcript(text):
    fillers = ["um", "uh", "you know", "like", "so"]
    for f in fillers:
        text = text.replace(f, "")
    return text

def chunk_text(text, max_tokens=1200, overlap=100, model="cl100k_base") -> List:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk = enc.decode(tokens[start:end])
        chunks.append(chunk)
        start += max_tokens - overlap

    return chunks



class Summarizer:

    def __init__(self, model:str="openai/gpt-oss-120b", LLM_API_KEY:str=GROQ_API_KEY, LLM_BASE_URL:str=GROQ_BASE_URL):
        """By default using Groq LLM with model openai/gpt-oss-120b"""
        
        self.llm = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        self.model = model
        self.chunking_model = "openai/gpt-oss-20b"
        self.transcript = ""
        logger.info("Summarizer object initialized")

    def set_transcript(self, transcript:str):
        self.transcript += transcript


    # def system_prompt(self):

    #     system_prompt = f"You are a helpful assistant. Your job is to summarize the youtube video transcript. Generate a short and crisp summary for the transcript provided keeping all the necessary details."
        
    #     original_length = len(self.transcript)
    #     logger.info(f"Length of transcript before cleaning: {original_length}")
        
    #     self.transcript = clean_transcript(self.transcript)
    #     length_after_cleaning = len(self.transcript)

    #     logger.info(f"Length of transcript after cleaning: {length_after_cleaning}")
    #     logger.info(f"Percentage reduction: {round((1-length_after_cleaning/original_length)*100, 2)} %")
        
    #     system_prompt += f"Transcript: {self.transcript}"

    #     logger.info(f"System Prompt head: {system_prompt[:100]}...")
    #     logger.info(f"System Prompt tail: ...{system_prompt[-150:]}")
        
    #     return system_prompt

    def summarize_chunk(self, chunk:str):
        messages = [
            {"role": "system", "content": "Summarize the following transcript part concisely into paragraphs. Do not create tables."},
            {"role": "user", "content": chunk}
        ]

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2
        )

        return response.choices[0].message.content

    def generate_chunk_summaries(self, chunks:List) -> List:
        chunk_summaries = []
        for chunk in chunks:
            chunk_summary = self.summarize_chunk(chunk)
            chunk_summaries.append(chunk_summary)
            time.sleep(1.5)
        return chunk_summaries


    def summarize(self):
        
        original_length = len(self.transcript)
        logger.info(f"Length of transcript before cleaning: {original_length}")

        self.transcript = clean_transcript(self.transcript)
        length_after_cleaning = len(self.transcript)
        
        logger.info(f"Length of transcript after cleaning: {length_after_cleaning}")
        # logger.info(f"Percentage reduction: {round((1-length_after_cleaning/original_length)*100, 2)} %")

        logger.info(f"Starting token-based chunking of the video transcript. Using model: {self.chunking_model}")        
        all_chunks = chunk_text(text=self.transcript, max_tokens=1200, overlap=100, model=self.chunking_model)

        logger.info(f"Chunks generated successfully. Length : {len(all_chunks)}")
        chunk_summaries = self.generate_chunk_summaries(chunks=all_chunks)

        final_prompt = """
            You are summarizing a YouTube video with help of chunked transcript of the video.
            Combine the following partial summaries of chunks into one clear, structured final summary. Avoid using tabular formats in summary. Keep in paragraphs. Use <br> for next line instead of \\n.
        """

        messages = [{"role": "system", "content": final_prompt},
                    {"role": "user", "content": "\n".join(chunk_summaries)}]
        logger.debug(f"Messages sending to LLM: {messages}")
        
        logger.info(f"Combining chunk summaries.")
        response = self.llm.chat.completions.create(model=self.model, 
                                                    messages=messages,
                                                    temperature=0.2)
        
        reply = response.choices[0].message.content 

        return reply


# if __name__  == "__main__":

#     # video_id = get_video_id_from_link(video_link)
#     pass 
