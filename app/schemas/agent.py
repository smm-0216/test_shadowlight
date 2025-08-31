from typing import Any, Dict, List, Union

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: Union[List[Dict[str, Any]], str]
