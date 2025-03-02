"""
Complete the configuration and rename this file to configs.py
"""
from backend.__types__ import QQBotConfig

configs = QQBotConfig(
    LISTENING_PORT = 3000, # Accepts event reports from OneBot

    HISTORY_SIZE = 64,      # Recent messages that the bot would remember 

    GROUP_ID = 114514,      # The group where the bot works
    SELF_ID = 1919,         # The client from which the OneBot sends reports 
    BOT_ID = 1919,          # The ID for the bot
    BOT_NAME = "BOT",       # The name of the bot

    ONEBOT_API_URL = "http://127.0.0.1:3001",   # The URL for the OneBot API
                                                # to send messages to the QQ client  

    OPENAI_API_URL = "https://api.openai.com/v1",
    OPENAI_API_TOKEN = "YOUR OPENAI API TOKEN",
    OPEN_AI_MODEL_ID = "gpt-4o",
    MORE_INFO = "YOUR EXTRA INFO FOR THE BOT",
    TEMPERATURE = 2.0,

    KUUKI_READER_API_URL = "https://api.openai.com/v1",
    KUUKI_READER_API_TOKEN = "YOUR OPENAI API TOKEN",
    KUUKI_READER_MODEL_ID = "gpt-4o",

    IMAGE_UNDERSTANDING_API_URL = "https://api.openai.com/v1",
    IMAGE_UNDERSTANDING_API_TOKEN = "YOUR OPENAI API TOKEN",
    IMAGE_UNDERSTANDING_MODEL_ID = "gpt-4-turbo", # The model must support image url input

    LOG_LEVEL = "DEBUG"
)