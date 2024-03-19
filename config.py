from pydantic_settings import BaseSettings


class TelegramConfig(BaseSettings):

    BASE_URL: str
    BOT_TOKEN: str
    CHAT_ID: str
    CHANNEL_CHAT_ID: str
    CLEAR_INTERVAL: int

    @property
    def api_url(self):
        return f"{self.BASE_URL}{self.BOT_TOKEN}/"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

config = TelegramConfig()