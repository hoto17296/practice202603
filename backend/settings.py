from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    password_pepper: str
    session_key: str = "session"
    jwt_private_key: str


settings = Settings()  # pyright: ignore[reportCallIssue]
