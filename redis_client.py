import os
import redis
from dotenv import load_dotenv

load_dotenv()


# ----------------------------------------------------
# Redis Connection
# ----------------------------------------------------

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True
)


# ----------------------------------------------------
# Test Redis Connection
# ----------------------------------------------------

def test_redis_connection():

    try:

        redis_client.ping()

        return True

    except redis.exceptions.RedisError:

        return False


# ----------------------------------------------------
# LOGIN SESSION
# ----------------------------------------------------

def create_login_session(email):

    key = f"bookrag:session:{email}"

    redis_client.setex(
        key,
        3600,
        "logged_in"
    )


def check_login_session(email):

    key = f"bookrag:session:{email}"

    return redis_client.exists(key) == 1


def delete_login_session(email):

    key = f"bookrag:session:{email}"

    redis_client.delete(key)


# ----------------------------------------------------
# RESET TOKEN
# ----------------------------------------------------

def save_reset_token(token, email):

    key = f"bookrag:reset:{token}"

    redis_client.setex(
        key,
        300,
        email
    )


def get_reset_token_email(token):

    key = f"bookrag:reset:{token}"

    return redis_client.get(key)


def delete_reset_token(token):

    key = f"bookrag:reset:{token}"

    redis_client.delete(key)