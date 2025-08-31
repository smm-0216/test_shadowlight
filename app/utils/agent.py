import os

from vanna.openai import OpenAI_Chat
from vanna.vannadb import VannaDB_VectorStore


class Agent(VannaDB_VectorStore, OpenAI_Chat):
    def __init__(self):
        VANNA_MODEL = os.getenv("VANNA_MODEL")
        VANNA_API_KEY = os.getenv("VANNA_API_KEY")
        DEFAULT_CONFIG = {
            'api_key': os.getenv("OPENAI_KEY"),
            'model': 'gpt-4o'
        }
        VannaDB_VectorStore.__init__(self, vanna_model=VANNA_MODEL, vanna_api_key=VANNA_API_KEY, config=DEFAULT_CONFIG)
        OpenAI_Chat.__init__(self, config=DEFAULT_CONFIG)
        
