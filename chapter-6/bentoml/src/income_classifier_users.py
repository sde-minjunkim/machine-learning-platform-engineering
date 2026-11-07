from pydantic import BaseModel


class IncomeClassifierUsers(BaseModel):
    user_id: str
