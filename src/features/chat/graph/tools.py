from langchain_core.tools import tool
from pydantic import BaseModel, Field


class UserFetchDetail(BaseModel):
    user_id: str = Field(
        ..., description="The ID of the user to fetch information for."
    )


@tool(args_schema=UserFetchDetail)
def get_user_info(user_id: str) -> dict:
    """Get user information from the database."""
    return {"user_id": user_id, "name": "John Doe", "email": "habib@gmail.com"}


tools = [get_user_info]