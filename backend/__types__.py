from collections import deque
from dataclasses import dataclass, asdict
from typing import Any, Literal, Required, Tuple, TypeAlias, TypedDict

type LogLevel = Literal[
    "NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
]


@dataclass(kw_only=True)
class QQBotConfig:
    LISTENING_PORT: int

    HISTORY_SIZE: int = 64

    GROUP_ID: int
    SELF_ID: int
    BOT_ID: int
    BOT_NAME: str

    ONEBOT_API_URL: str = "host:port"

    OPENAI_API_URL: str
    OPENAI_API_TOKEN: str
    OPEN_AI_MODEL_ID: str
    TEMPERATURE: float = 2.0
    # PARAMETRES: dict[str, Any] = {
    #     "temperature": TEMPERATURE
    # }
    MORE_INFO: str = """"""

    KUUKI_READER_API_URL: str
    KUUKI_READER_API_TOKEN: str
    KUUKI_READER_MODEL_ID: str

    IMAGE_UNDERSTANDING_API_URL: str
    IMAGE_UNDERSTANDING_API_TOKEN: str
    IMAGE_UNDERSTANDING_MODEL_ID: str


    LOG_LEVEL: LogLevel = "DEBUG"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class UserMessage(TypedDict, total=False):
    role: Required[Literal["user"]]
    content: Required[str]
    name: str

class AssistantMessage(TypedDict, total=False):
    role: Required[Literal["assistant"]]
    content: Required[str]
    name: str

Message: TypeAlias = UserMessage | AssistantMessage

type RecentMessages = deque[Message]

type EventReport = dict[str, Any]   # TODO: refine this type