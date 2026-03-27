from pydantic import BaseModel


class NarrativeEventRequest(BaseModel):
    action: str
    user_id: str
