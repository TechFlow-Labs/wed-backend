from fastapi_mail import  ConnectionConfig
from environs import Env

env = Env()
env.read_env()

connection = ConnectionConfig(
    MAIL_USERNAME=env.str("MAIL_USERNAME"),
    MAIL_PASSWORD=env.str("MAIL_PASSWORD"),
    MAIL_FROM=env.str("MAIL_FROM"),
    MAIL_PORT=env.int("MAIL_PORT"),
    MAIL_SERVER=env.str("MAIL_SERVER"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)