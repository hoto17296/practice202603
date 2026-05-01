from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    password_pepper: str


settings = Settings()  # pyright: ignore[reportCallIssue]
