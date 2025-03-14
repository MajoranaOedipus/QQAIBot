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
import logging

from backend.backend import create_app
from configs import configs

logging.basicConfig(level=configs.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    app = create_app(configs)
    app.run(host='0.0.0.0', port=configs.LISTENING_PORT)