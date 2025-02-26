# QQBot

This is a QQ Bot that integrates with OpenAI-compatible APIs to participate in group chats. It requires LiteLoaderNTQQ and OneBot to function properly. 

## Installation

To install the dependencies for this project, run:

```bash
pip install -r requirements.txt
```

For the scripts to run, you will need a working installation of NTQQ, with the LiteLoader and OneBot plugin and enabled. 

## Configuration

Complete the QQBotConfig_sample.py file and rename it to QQBotConfig.py. 


## Running the Bot

To start the bot, use the following command:

```bash
python main.py > log.txt
```

The log is super verbose and all your sensitive data will be printed there, so be sure redirect it and do not post it online before cleaning it up.

## Features

The features are simple for now: it listens to the HTTP signal sent by OneBot, maintaining a message history of length HISTORY_SIZE (`QQBotConfig.py`); 
if the bot is triggered (mentioned or with 10% random chance), it will send a prompt prepared with the triggering message, message history with the prompt template provided by `prompts.py` to the OpenAI API, and send the response back to the chat.

The project is still under development, so nothing is guaranteed to work. And changes are expected to happen.


## License

This project is licensed under the GPL-3.0-or-later License - see the LICENSE file for details.

```
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
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
```