from time import localtime, strftime
import unittest
from unittest.mock import patch, MagicMock
from collections import deque
import json
import sys
import os
from datetime import datetime

from backend.__types__ import EventReport
from backend.backend import (
    process_group_msg, 
    triggered_with, 
    generate_response, 
    make_chat_record,
    get_text_from_message,
    send_group_message,
    was_bot_mentioned
)

from configs_template import configs


class QQBotTest(unittest.TestCase):
    def setUp(self):
        self.configs = configs
        self.recent_messages = deque(maxlen=10)
        
        # 创建一个示例消息
        self.sample_message: EventReport
        self.sample_message = {
            "self_id": 1919,
            "user_id": 810,
            "time": 1739211984,
            "message_id": 893,
            # "message_seq": MESSAGE_SEQ,
            "message_type": "group",
            "sender": {
                "user_id": 810,
                "nickname": "QQ 昵称",
                "card": "群昵称",
                "role": "owner",
                "title": "",
            },
            "raw_message": f"[CQ:at,qq={1919},name=BOT] 你是坏猫",
            "font": 14,
            "sub_type": "normal",
            "message": [
                {"type": "at", "data": {"qq": "BOT_ID", "name": "BOT"}},
                {"type": "text", "data": {"text": " 你是坏猫"}},
            ],
            "message_format": "array",
            "post_type": "message_sent",
            "group_id": 114514,
            # "target_id": 114514,
        }

    @patch('backend.backend.was_bot_mentioned')
    def test_triggered_with(self, mock_was_bot_mentioned):
        """测试触发检测功能"""
        mock_was_bot_mentioned.return_value = True
        
        result = triggered_with(self.sample_message, self.recent_messages, self.configs)
        
        self.assertEqual(result, "reply")
        mock_was_bot_mentioned.assert_called_once()

    @patch('backend.backend.get_text_from_message')
    def test_make_chat_record(self, mock_get_text):
        """测试聊天记录生成功能"""
        mock_get_text.return_value = "你好，@BOT"
        t = strftime("%d %b %H:%M:%S", localtime(self.sample_message["time"]))
        
        result = make_chat_record(self.sample_message, self.configs)
        
        self.assertEqual(result, {
            "role": "user",
            "content": f"({t}) 群昵称: 你好，@BOT",
            "name": "群昵称"
            })
        mock_get_text.assert_called_once()

    def test_was_bot_mentioned(self):
        """测试@检测功能"""
        self.sample_message["raw_message"] = "[CQ:at,qq=1919,name=BOT] 你好"
        result = was_bot_mentioned(self.sample_message, 1919)
        self.assertTrue(result)

        self.sample_message["raw_message"] = "你好啊"
        result = was_bot_mentioned(self.sample_message, 1919)
        self.assertFalse(result)

    @patch('requests.post')
    def test_send_group_message(self, mock_post):
        """测试发送消息功能"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_group_message("测试消息", self.configs, mode="reply", msg_id="123456")
        
        mock_post.assert_called_once()
        # 检查 URL 是否正确
        args, kwargs = mock_post.call_args
        # Check if URL contains either localhost or 127.0.0.1 with port 3001
        self.assertIn(args[0], ["http://localhost:3001/send_group_msg", "http://127.0.0.1:3001/send_group_msg"])

    @patch('backend.backend.was_bot_mentioned')
    @patch('backend.backend.triggered_with')
    @patch('backend.backend.generate_response')
    @patch('backend.backend.send_group_message')
    def test_process_group_msg(self, mock_send_group_message, mock_generate, mock_triggered, mock_was_mentioned):
        """测试群消息处理功能"""
        # 设置模拟返回值
        mock_triggered.return_value = "reply"
        mock_generate.return_value = "测试回复"
        
        # 执行测试函数
        process_group_msg(self.sample_message, self.recent_messages, self.configs)
        
        # 验证模拟函数是否被正确调用
        mock_triggered.assert_called_once_with(self.sample_message, self.recent_messages, self.configs)
        mock_generate.assert_called_once()
        mock_send_group_message.assert_called_once_with("测试回复", self.configs, mode="reply", msg_id=self.sample_message["message_id"])
    
        
    def test_get_text_from_message(self):
        """测试从消息中提取文本功能"""
        # 测试标准消息格式
        message = [
            {"type": "at", "data": {"qq": "1919", "name": "BOT"}},
            {"type": "text", "data": {"text": " 你好机器人"}}
        ]
        result = get_text_from_message(message, self.configs)
        self.assertEqual(result, "@BOT 你好机器人")
        
        # 测试仅文本消息
        message = [{"type": "text", "data": {"text": "纯文本消息"}}]
        result = get_text_from_message(message, self.configs)
        self.assertEqual(result, "纯文本消息")

if __name__ == '__main__':
    unittest.main()