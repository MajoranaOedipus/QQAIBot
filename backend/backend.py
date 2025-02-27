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
from typing import Literal, Tuple
from flask import Flask, request, jsonify
import requests

from collections import deque
import logging
from time import localtime, strftime

from .QQBotConfig import HISTORY_SIZE, BOT_ID, SELF_ID, BOT_NAME, GROUP_ID
from .QQBotConfig import LOG_LEVEL
from .QQBotConfig import LISTENING_PORT, API_URL
from .prompts import SYSTEM_PROMPT_HEAD, REPLY_PROMPT, COMMENT_PROMPT
from .ai_client import get_ai_response, get_image_understanding, kuuki_reader, image_understanding_client

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)


recent_messages: deque[Tuple[str, str]] = deque(maxlen=HISTORY_SIZE)

@app.route('/', methods=['POST'])
def root():
    """Prints the received data and returns a success message."""
    data: str = request.get_json()
    
    logging.debug(f"Received: {data}")

    process(data)
        
    return jsonify({"status": "success", "message": "Data received"})

def process(data):
    if data["self_id"] == BOT_ID and "message_type" in data:
        if data["message_type"] == "group" and data["group_id"] == GROUP_ID:
            process_group(data)

def process_group(data):
    chat_time = strftime("%d %b %H:%M:%S", localtime(data["time"]))
    working_memory = (chat_time, make_chat_record(data))

    triggered_mode = triggered_with(data)
    if triggered_mode:
        logging.info(f"Bot triggered with: {working_memory}")
        response = generate_response(working_memory, recent_messages, triggered_mode)
        logging.debug(f"Bot response: {response}")
        send_message(response, mode=triggered_mode, msg_id=data["message_id"])
    recent_messages.append(working_memory)
    logging.debug(f"Recent messages:\n\t{recent_messages[0]}\n\t...\n\t{recent_messages[-1]}")

def triggered_with(data) -> Literal["", "reply", "normal"]:
    if data["sender"]["user_id"] == BOT_ID:
        return ""
    
    if was_bot_mentioned(data):
        return "reply"
    
    message = data["raw_message"]
    if "柔柔" in message and should_bot_respond(data):
        return "reply"

    from random import randint
    is_triggered = (90 < randint(0, 100)) and SELF_ID != data["sender"]["user_id"]
    if is_triggered:
        return "normal"
    else:
        return ""

def should_bot_respond(data) -> bool:
    chat_time = strftime("%d %b %H:%M:%S", localtime(data["time"]))
    message = (chat_time, make_chat_record(data))
    kuuki_for_respond = kuuki_reader(
        prepare_user_prompt_comment(
            message,
            recent_messages
        )
    )
    if "是" in kuuki_for_respond:
        logging.info(f"Kuuki reader decides that bot should respond to: {message}")
        return True
    elif "否" in kuuki_for_respond:
        logging.debug(f"Kuuki reader decides that bot should not respond to: {message} with ({kuuki_for_respond})")
        return False
    else:
        logging.warning(
            f"Kuuki reader failed to decide with '{kuuki_for_respond}' for '{message}'"
        )
        return False

def was_bot_mentioned(data) -> bool:
    message = data["raw_message"]
    if f"[CQ:at,qq={BOT_ID}" in message:
        return True
    return False


type Message = dict[str, str | dict[str, str]]
type MessageList = list[Message]
def get_text_from_message(message_list: MessageList) -> str:
    text = ""
    for message in message_list:
        if message["type"] == "text":
            text += message["data"]["text"]
        elif message["type"] == "at":
            if message["data"]["qq"] == str(BOT_ID):
                text += f"@{BOT_NAME}"
            else:
                text += f"@{message['data']['name']}"
        elif message["type"] == "image":
            text += f"""[图片: {
                get_image_understanding(message['data']['url'])
                }]""" 
    return text

def make_chat_record(data) -> str:
    sender: str
    if data["sender"]["user_id"] == BOT_ID:
        sender = BOT_NAME
    else:
        if "card" in data["sender"] and data["sender"]["card"]:
            sender = data["sender"]["card"]
        else:
            sender = data["sender"]["nickname"]
    text = get_text_from_message(data["message"])
    return f"{sender}: {text}"

def send_message(
        message: str, 
        mode: Literal["reply", "normal"] = "normal", 
        msg_id: str|None = None
    ) -> None:
    message_constructed: list[dict[str, dict[str, str]]] = []
    if mode == "reply":
        message_constructed.append(
            {
                "type": "reply",
                "data": {
                    "id": msg_id
                }
            }
        )

    message_constructed.append(
        {
            "type": "text",
            "data": {
                "text": message
            }
        }
    )
    payload = {
        "group_id": GROUP_ID,
        "message": message_constructed,
        "auto_escape": False
    }
    headers = {
        # 'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }

    # 发送 POST 请求
    response = requests.post(API_URL + "/send_group_msg", json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        logging.info(f"Bot sent to {GROUP_ID}: {message} with mode {mode}")
    else:
        logging.error(f"Bot failed sending to group {GROUP_ID} with code {response.status_code}. Response: {response.text}")

def generate_response(
        message: str, 
        recent_messages: deque[str],
        respond_type: Literal["reply", "normal"] = "reply"
    ) -> str:
    if respond_type == "reply":
        user_prompt = prepare_user_prompt_reply(message, recent_messages)
    elif respond_type == "normal":
        user_prompt = prepare_user_prompt_comment(message, recent_messages)
    else:
        logging.error(f"Invalid respond type: {respond_type}")
        return "抱歉喵，母星给我发了些奇怪的信号……"
    return get_ai_response(prepare_system_prompt(respond_type), user_prompt)

def prepare_system_prompt(mode: Literal["reply", "normal"]):
    if mode == "reply":
        return SYSTEM_PROMPT_HEAD + REPLY_PROMPT
    else:
        return SYSTEM_PROMPT_HEAD + COMMENT_PROMPT


def prepare_user_prompt_reply(message: Tuple[str, str], recent_messages: deque[Tuple[str, str]]) -> str:
    recent_messages_genearator = (f"({time}) {msg}" for time, msg in recent_messages)
    return f"""\
recent_messages: [
{",\n".join(recent_messages_genearator)}
]
message_to_reply:
({message[0]}) {message[1]}\
"""

def prepare_user_prompt_comment(message: Tuple[str, str], recent_messages: deque[Tuple[str, str]]) -> str:
    recent_messages_genearator = (f"({time}) {msg}" for time, msg in recent_messages)
    return f"""\
recent_messages: [
{",\n".join(recent_messages_genearator)}
]
last_message:
    ({message[0]}) {message[1]})\
"""

def main():
    app.run(host='0.0.0.0', port=LISTENING_PORT)


