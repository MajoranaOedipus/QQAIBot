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

from .__types__ import QQBotConfig
from .prompts import IMAGE_UNDERSTANDING_PROMPT, READ_KUUKI_PROMPT_TEMPLATE

import logging


def get_ai_response(
        system_prompt: str, 
        user_prompt: str,
        configs: QQBotConfig
        ) -> str:
    OPENAI_API_TOKEN, OPENAI_API_URL, OPEN_AI_MODEL_ID = (
        configs.OPENAI_API_TOKEN, configs.OPENAI_API_URL, configs.OPEN_AI_MODEL_ID
    )
    chatbot_client = OpenAI(api_key=OPENAI_API_TOKEN, base_url=OPENAI_API_URL)

    logging.debug(f"Generates AI response with system prompt of length {len(system_prompt)} and user prompt of length {len(user_prompt)}")
    respond = chatbot_client.chat.completions.create(
                model = OPEN_AI_MODEL_ID,
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                    ]
        )
    logging.debug(f"AI response: {respond}")
    if respond.choices and respond.choices[0].message.content is not None:
        return respond.choices[0].message.content
    else:
        logging.error(f"No response from {OPEN_AI_MODEL_ID}")
        return "抱歉喵，我和母星的连接好像中断了……"



def get_kuuki(user_prompt: str, configs: QQBotConfig) -> str:
    KUUKI_READER_API_TOKEN, KUUKI_READER_API_URL, KUUKI_READER_MODEL_ID = (
        configs.KUUKI_READER_API_TOKEN, 
        configs.KUUKI_READER_API_URL, 
        configs.KUUKI_READER_MODEL_ID
    )
    kuuki_reader_client = OpenAI(api_key=KUUKI_READER_API_TOKEN, base_url=KUUKI_READER_API_URL)
    logging.debug(f"Generates Kuuki Reader response from messgae {user_prompt}")
    respond = kuuki_reader_client.chat.completions.create(
        model=KUUKI_READER_MODEL_ID,
        messages=[
            {
                "role": "system", 
                "content": READ_KUUKI_PROMPT_TEMPLATE.format(**configs.to_dict())
            },
            {"role": "user", "content": user_prompt}
        ]
    )
    if respond.choices and respond.choices[0].message.content is not None:
        return respond.choices[0].message.content
    else:
        logging.error(f"No response from {KUUKI_READER_MODEL_ID}")
        return "空气读不出来喵……"




def get_image_understanding(image_url: str, configs: QQBotConfig) -> str:
    IMAGE_UNDERSTANDING_API_TOKEN = configs.IMAGE_UNDERSTANDING_API_TOKEN
    IMAGE_UNDERSTANDING_API_URL = configs.IMAGE_UNDERSTANDING_API_URL
    IMAGE_UNDERSTANDING_MODEL_ID = configs.IMAGE_UNDERSTANDING_MODEL_ID

    image_understanding_client = OpenAI(api_key=IMAGE_UNDERSTANDING_API_TOKEN, base_url=IMAGE_UNDERSTANDING_API_URL)
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
    
    if respond.choices and respond.choices[0].message.content is not None:
        return respond.choices[0].message.content
    else:
        logging.error(f"No response from {IMAGE_UNDERSTANDING_MODEL_ID}")
        return "这里有一张图片，但是看不懂喵……"