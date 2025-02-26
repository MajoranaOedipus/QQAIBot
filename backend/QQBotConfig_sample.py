"""
Complete the configuration and rename this file to QQBotConfig.py
"""

from enum import Enum
from typing import Literal


LISTENING_PORT: int =

HISTORY_SIZE: int = 64

GROUP_ID: int =
SELF_ID: int =
BOT_ID: int =
BOT_NAME: str =

API_URL = "host:port"

OPENAI_API_URL =
OPENAI_API_TOKEN =
OPEN_AI_MODEL_ID =

MORE_INFO =

TEMPERATURE = 2
PARAMETRES = {
    "temperature": TEMPERATURE
}

type LogLevel = Literal[
    "NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    ]
LOG_LEVEL: LogLevel = "DEBUG"
