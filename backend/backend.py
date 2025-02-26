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
from flask import Flask, request, jsonify
import requests

from collections import deque
import logging
from time import localtime, strftime

from .QQBotConfig import HISTORY_SIZE, BOT_ID, SELF_ID, BOT_NAME, GROUP_ID
from .QQBotConfig import LOG_LEVEL
from .QQBotConfig import LISTENING_PORT, API_URL
from .ai_client import get_ai_response

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)


recent_messages: deque[Tuple[str, str]] = deque(maxlen=HISTORY_SIZE)

@app.route('/', methods=['POST'])
def root():
    """Prints the received data and returns a success message."""
    data: str = request.get_json()
    """
    data looks like
    {'self_id': SELF_ID, 'user_id': USER_ID, 'time': 1739211984, 'message_id': MESSAGE_ID, 'message_seq': MESSAGE_SEQ, 'message_type': 'group', 'sender': {'user_id': USER_ID, 'nickname': 'QQ 昵称', 'card': '群名', 'role': 'owner', 'title': ''}, 'raw_message': '[CQ:at,qq=BOT_ID,name=酷酷猫猫虫] 你是坏猫', 'font': 14, 'sub_type': 'normal', 'message': [{'type': 'at', 'data': {'qq': 'BOT_ID', 'name': '酷酷猫猫虫'}}, {'type': 'text', 'data': {'text': ' 你是坏猫'}}], 'message_format': 'array', 'post_type': 'message_sent', 'group_id': GROUP_ID, 'target_id': GROUP_ID}
    """
    logging.debug(f"Received: {data}")
    if data["self_id"] == BOT_ID and "message_type" in data:
        
        if data["message_type"] == "group" and data["group_id"] == GROUP_ID:
            
            
            chat_time = strftime("%d %b %H:%M:%S", localtime(data["time"]))
            chat_record = (chat_time, make_chat_record(data))

            if triggered(data["raw_message"], data["sender"]["user_id"]):
                logging.info(f"Bot triggered with: {chat_record}")
                response = generate_response(data["sender"]["user_id"], chat_record, recent_messages)
                logging.debug(f"Bot response: {response}")
                send_message(response)
                # send_message("我收到了啦，烦死了，我还没搞定调用 API 呢")    # TODO
            recent_messages.append(chat_record)
            logging.debug(f"Recent messages: {recent_messages}")
            

        
    return jsonify({"status": "success", "message": "Data received"})

def triggered(data) -> bool:
    message = data["raw_message"]
    from random import randint
    is_triggered = (80 < randint(0, 100)) and SELF_ID != data["sender"]["user_id"]
    return is_triggered or was_bot_mentioned(message)

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

def send_message(message: str) -> None:
    payload = {
        "group_id": GROUP_ID,
        "message": message,
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
        logging.info(f"Bot sent to {GROUP_ID}: {message}")
    else:
        logging.error(f"Bot failed sending to group {GROUP_ID} with code {response.status_code}. Response: {response.text}")

def generate_response(sender_id: int, message: str, recent_messages: deque[str]) -> str:
    return f"[CQ:reply,id={sender_id}]{get_ai_response(message, recent_messages)}"

def main():
    app.run(host='0.0.0.0', port=LISTENING_PORT)


