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
from typing import Tuple
from QQBotConfig import OPENAI_API_TOKEN, OPEN_AI_MODEL_ID, OPENAI_API_URL, PARAMETRES, BOT_NAME
from prompts import SYSTEM_PROMPT
from QQBotConfig import LOG_LEVEL
from openai import OpenAI
from collections import deque
from time import localtime, strftime
import logging

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')


openai_client = OpenAI(api_key=OPENAI_API_TOKEN, base_url=OPENAI_API_URL)

def get_ai_response(message: str, recent_messages: deque[str]) -> str:
    user_prompt = prepare_user_prompt(message, recent_messages)
    logging.debug(f"User prompt: {user_prompt}")
    respond = openai_client.chat.completions.create(
                model = OPEN_AI_MODEL_ID,
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                    ]
        )
    logging.debug(f"AI response: {respond}")
    if respond.choices:
        return respond.choices[0].message.content
    else:
        logging.ERROR(f"No response from AI")
        return "抱歉喵，我和母星的连接好像中断了……"
        

def prepare_user_prompt(message: Tuple[str, str], recent_messages: deque[Tuple[str, str]]) -> str:
    recent_messages_genearator = (f"({time}) {msg}" for time, msg in recent_messages)
    return f"""\
recent_messages: [
{",\n".join(recent_messages_genearator)}
]
message_to_reply:
({message[0]}) {message[1]}\
"""

if __name__ == "__main__":
    message = (strftime("%d %b %H:%M:%S", localtime()), f"Alice: 你好！{BOT_NAME}，你给大家介绍一下你自己吧，和大家每个人都打个招呼。")
    recent_messages = deque([
        (strftime("%d %b %H:%M:%S", localtime()), "Bob: 你好！"), 
        (strftime("%d %b %H:%M:%S", localtime()), "Cowboy: 你好！")
        ])

    print(get_ai_response(message, recent_messages))
