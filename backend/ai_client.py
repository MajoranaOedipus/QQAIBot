"""\
    QQAIBot - A QQ Bot that integrates with OpenAI-compatible APIs to participate in group chats.
    Copyright (C) 2024  Majorana Oedipus (majoranaoedipus@posteo.org)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.\
"""
from openai import OpenAI

from .QQBotConfig import OPENAI_API_TOKEN, OPEN_AI_MODEL_ID, OPENAI_API_URL, PARAMETRES, BOT_NAME
from .QQBotConfig import KUUKI_READER_API_TOKEN, KUUKI_READER_MODEL_ID, KUUKI_READER_API_URL
from .QQBotConfig import IMAGE_UNDERSTANDING_API_TOKEN, IMAGE_UNDERSTANDING_MODEL_ID, IMAGE_UNDERSTANDING_API_URL
from .QQBotConfig import LOG_LEVEL

from .prompts import IMAGE_UNDERSTANDING_PROMPT, SYSTEM_PROMPT_HEAD, READ_KUUKI_PROMPT

from collections import deque
from time import localtime, strftime
import logging

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

chatbot_client = OpenAI(api_key=OPENAI_API_TOKEN, base_url=OPENAI_API_URL)

def get_ai_response(system_prompt: str, user_prompt: str) -> str:
    # user_prompt = prepare_user_prompt(message, recent_messages)
    # logging.debug(f"User prompt: {user_prompt}")
    logging.debug(f"Generates AI response with system prompt of length {len(system_prompt)} and user prompt of length {len(user_prompt)}")
    respond = chatbot_client.chat.completions.create(
                model = OPEN_AI_MODEL_ID,
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                    ]
        )
    logging.debug(f"AI response: {respond}")
    if respond.choices:
        return respond.choices[0].message.content
    else:
        logging.ERROR(f"No response from {OPEN_AI_MODEL_ID}")
        return "抱歉喵，我和母星的连接好像中断了……"

kuuki_reader_client = OpenAI(api_key=KUUKI_READER_API_TOKEN, base_url=KUUKI_READER_API_URL)

def kuuki_reader(user_prompt: str) -> str:
    logging.debug(f"Generates Kuuki Reader response from messgae {user_prompt}")
    respond = kuuki_reader_client.chat.completions.create(
        model=KUUKI_READER_MODEL_ID,
        messages=[
            {"role": "system", "content": READ_KUUKI_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )
    if respond.choices:
        return respond.choices[0].message.content
    else:
        logging.ERROR(f"No response from {KUUKI_READER_MODEL_ID}")
        return "空气读不出来喵……"


image_understanding_client = OpenAI(api_key=IMAGE_UNDERSTANDING_API_TOKEN, base_url=IMAGE_UNDERSTANDING_API_URL)

def get_image_understanding(image_url: str) -> str:
    respond = image_understanding_client.chat.completions.create(
        model=IMAGE_UNDERSTANDING_MODEL_ID,  
        messages=[
                {"role": "user","content": [
                        {"type": "text", "text": IMAGE_UNDERSTANDING_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ]
    )
    
    if respond.choices:
        return respond.choices[0].message.content
    else:
        logging.ERROR(f"No response from {KUUKI_READER_MODEL_ID}")
        return "这里有一张图片，但是看不懂喵……"


if __name__ == "__main__":
    message = (strftime("%d %b %H:%M:%S", localtime()), f"Alice: 你好！{BOT_NAME}，你给大家介绍一下你自己吧，和大家每个人都打个招呼。")
    recent_messages = deque([
        (strftime("%d %b %H:%M:%S", localtime()), "Bob: 你好！"), 
        (strftime("%d %b %H:%M:%S", localtime()), "Cowboy: 你好！")
        ])

    print(get_ai_response(message, recent_messages))
