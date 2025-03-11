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
from typing import Any, Literal
from flask import Flask, request, jsonify
import requests

from collections import deque
import logging
from time import localtime, strftime

from .__types__ import AssistantMessage, QQBotConfig, RecentMessages, EventReport, Message, UserMessage

from .prompts import SYSTEM_PROMPT_HEAD_TEMPLATE, REPLY_PROMPT, COMMENT_PROMPT
from .ai_client import get_ai_response, get_image_understanding, get_kuuki


def create_app(configs: QQBotConfig):
    recent_messages: RecentMessages = deque(maxlen=configs.HISTORY_SIZE)
    
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def root():
        """Prints the received data and returns a success message."""
        event_report: EventReport = request.get_json()
        
        logging.debug(f"Received: {event_report}")

        process(event_report, recent_messages, configs)
            
        return jsonify({"status": "success", "message": "Data received"})

    return app

def process(
        event_report: EventReport, 
        recent_messages: RecentMessages, 
        configs: QQBotConfig
    ) -> None:
    BOT_ID, GROUP_ID = configs.BOT_ID, configs.GROUP_ID

    if (event_report["self_id"] == BOT_ID
        and "message_type" in event_report):
        if (event_report["message_type"] == "group"
            and event_report["group_id"] == GROUP_ID):
            process_group_msg(event_report, recent_messages, configs)

        if event_report["message_type"] == "private" and event_report["sender"]["user_id"] != BOT_ID:
            from os import getpid
            send_private_message(
                f"我在工作喵。我的 process id 是 {getpid()}", event_report["sender"]["user_id"], configs
            )

def process_group_msg(
        event_report: EventReport, 
        recent_messages: RecentMessages, 
        configs: QQBotConfig
    ) -> None:
    
    
    triggered_mode = triggered_with(event_report, recent_messages, configs)
    last_message: Message = make_chat_record(event_report, configs)
    recent_messages.append(last_message)
    if triggered_mode:
        logging.info(f"Bot triggered by {last_message} with mode {triggered_mode}")
        if triggered_mode == "clear":
            recent_messages.clear()
            logging.info("Recent messages cleared.")
        else:
            response = generate_response(recent_messages, configs, triggered_mode)
            logging.debug(f"Bot response: {response}")
            send_group_message(
                response, 
                configs, 
                mode=triggered_mode, 
                msg_id=event_report["message_id"])
    if recent_messages:
        logging.debug(f"Recent messages:\n\t{recent_messages[0]}\n\t...\n\t{recent_messages[-1]}")

def triggered_with(
        event_report: EventReport, 
        recent_messages: RecentMessages,
        configs: QQBotConfig
    ) -> Literal["", "reply", "normal", "clear"]:

    if event_report["raw_message"].startswith("/clear"):
        return "clear"

    BOT_ID, BOT_NAME = configs.BOT_ID, configs.BOT_NAME
    if event_report["sender"]["user_id"] == BOT_ID: # Bot should not respond to itself
        return ""
    
    # Sent from the user:

    if was_bot_mentioned(event_report, BOT_ID):
        return "reply"
    
    message = event_report["raw_message"]
    if BOT_NAME in message and should_bot_respond(event_report, recent_messages, configs):
        return "reply"

    from random import randint
    is_triggered = (90 < randint(0, 100)) and BOT_ID != event_report["sender"]["user_id"]
    if is_triggered:
        return "normal"
    else:
        return ""

def should_bot_respond(
        event_report: EventReport,
        recent_messages: RecentMessages,
        configs: QQBotConfig) -> bool:
    last_message = make_chat_record(event_report, configs)
    kuuki_for_respond = get_kuuki(
        last_message, recent_messages, configs
    )
    if "是" in kuuki_for_respond:
        logging.info(f"Kuuki reader decides that bot should respond to: {last_message}")
        return True
    elif "否" in kuuki_for_respond:
        logging.info(f"Kuuki reader decides that bot should not respond to: {last_message} with ({kuuki_for_respond})")
        return False
    else:
        logging.warning(
            f"Kuuki reader failed to decide with '{kuuki_for_respond}' for '{last_message}'"
        )
        return False

def was_bot_mentioned(event_report: EventReport, bot_id: int) -> bool:
    message = event_report["raw_message"]
    if f"[CQ:at,qq={bot_id}" in message:
        return True
    return False


type EventMessage = dict[str, Any]
type EventMessageList = list[EventMessage]
def get_text_from_message(message_list: EventMessageList, configs: QQBotConfig) -> str:
    BOT_ID, BOT_NAME = configs.BOT_ID, configs.BOT_NAME
    
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
                get_image_understanding(message['data']['url'], configs)
                }]""" 
    return text

def make_chat_record(event_report: EventReport, configs: QQBotConfig) -> Message:
    BOT_ID, BOT_NAME = configs.BOT_ID, configs.BOT_NAME
    role: Literal["user", "assistant"] = "user"
    sender: str

    chat_time = strftime("%d %b %H:%M:%S", localtime(event_report["time"]))
    if event_report["sender"]["user_id"] == BOT_ID:
        sender = BOT_NAME
        role = "assistant"
    else:
        if "card" in event_report["sender"] and event_report["sender"]["card"]:
            sender = event_report["sender"]["card"] # ``card'' for in-group nickname
        else:
            sender = event_report["sender"]["nickname"]
    text = get_text_from_message(event_report["message"], configs)
    content = f"({chat_time}) {sender}: {text}"

    match role:
        case "user":
            return UserMessage(role=role, content=content, name=sender)
        case "assistant":
            return AssistantMessage(role=role, content=content, name=sender)

def send_group_message(
        message: str, 
        configs: QQBotConfig,
        mode: Literal["reply", "normal"] = "normal", 
        msg_id: str|None = None
    ) -> None:
    GROUP_ID, ONEBOT_API_URL = configs.GROUP_ID, configs.ONEBOT_API_URL

    message_constructed: list[dict[str, str | dict[str, str|None]]] = []
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
    response = requests.post(ONEBOT_API_URL + "/send_group_msg", json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        logging.info(f"Bot sent to {GROUP_ID}: {message} with mode {mode}")
    else:
        logging.error(f"Bot failed sending to group {GROUP_ID} with code {response.status_code}. Response: {response.text}")

def send_private_message(message: str, user_id: int, configs: QQBotConfig) -> None:

    ONEBOT_API_URL = configs.ONEBOT_API_URL

    message_constructed: list[dict[str, str | dict[str, str|None]]] = []
    

    message_constructed.append(
        {
            "type": "text",
            "data": {
                "text": message
            }
        }
    )
    payload = {
        "user_id": user_id,
        "message": message_constructed,
        "auto_escape": False
    }
    headers = {
        # 'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }

    # 发送 POST 请求
    response = requests.post(ONEBOT_API_URL + "/send_private_msg", json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        logging.info(f"Bot sent to {user_id}: {message}")
    else:
        logging.error(f"Bot failed sending to {user_id} with code {response.status_code}. Response: {response.text}")


def generate_response(
        recent_messages: RecentMessages,
        configs: QQBotConfig,
        respond_type: Literal["reply", "normal"] = "reply",
    ) -> str:
    if respond_type not in ["reply", "normal"]:
        logging.error(f"Invalid response type: {respond_type}." 
                      + "Must be either 'reply' or 'normal'.")
        return "抱歉喵，母星给我发了些奇怪的信号……"
    return get_ai_response(
        prepare_system_prompt(respond_type, configs), 
        recent_messages, 
        configs
    )

def prepare_system_prompt(mode: Literal["reply", "normal"], configs: QQBotConfig) -> str:
    if mode == "reply":
        return SYSTEM_PROMPT_HEAD_TEMPLATE.format(**configs.to_dict()) + REPLY_PROMPT
    else:
        return SYSTEM_PROMPT_HEAD_TEMPLATE.format(**configs.to_dict()) + COMMENT_PROMPT





