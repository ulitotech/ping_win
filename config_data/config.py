from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str
    db_host: str
    db_user: str
    db_password: str


@dataclass
class TgBot:
    token: str
    admin_id:str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_id=env('ADMIN_ID'),
        ),
        db=DatabaseConfig(
            database=env('DATABASE'),
            db_host=env('DB_HOST'),
            db_user=env('DB_USER'),
            db_password=env('DB_PASSWORD')
        )
    )


if __name__ == '__main__':
    config = load_config('./.env')
    print('BOT_TOKEN:', config.tg_bot.token)
    print('BOT_TOKEN:', config.tg_bot.admin_id)
    print('DATABASE:', config.db.database)
    print('DB_HOST:', config.db.db_host)
    print('DB_USER:', config.db.db_user)
    print('DB_PASSWORD:', config.db.db_password)
