import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


load_dotenv()


class Config:
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'root')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'root')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'alerts_db')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    CONNECTION_URL = f'postgresql://{os.getenv("POSTGRES_USER", "root")}:{os.getenv("POSTGRES_PASSWORD", "root")}@{os.getenv("POSTGRES_HOST", "db")}:{os.getenv("POSTGRES_PORT", "5432")}/{ os.getenv("POSTGRES_DB", "alerts_db")}'

    @property
    def postgresql_engine(self):
        return create_engine(f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    def connection_url(self) -> str:
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
