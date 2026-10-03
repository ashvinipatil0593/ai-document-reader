import os
import re
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv


# =====================================================
# ENVIRONMENT
# =====================================================

load_dotenv()


# =====================================================
# MONGODB CONNECTION
# =====================================================

MONGO_URI = os.getenv("MONGO_URI")

MONGO_DB_NAME = os.getenv(
    "MONGO_DB_NAME",
    "book_rag_chatbot"
)


if not MONGO_URI:
    raise ValueError(
        "MONGO_URI is missing from .env file"
    )


client = MongoClient(
    MONGO_URI
)

db = client[
    MONGO_DB_NAME
]

users_collection = db["users"]


# =====================================================
# PASSWORD HASHING
# =====================================================

def hash_password(password: str) -> str:

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# =====================================================
# EMAIL VALIDATION
# =====================================================

def is_valid_email(
    email: str
) -> bool:

    pattern = (
        r"^[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}$"
    )

    return bool(
        re.match(
            pattern,
            email
        )
    )


# =====================================================
# PASSWORD VALIDATION
# =====================================================

def validate_password(
    password: str
):

    if len(password) < 8:

        return (
            False,
            "Password must contain at least 8 characters."
        )

    if not re.search(
        r"[A-Z]",
        password
    ):

        return (
            False,
            "Password must contain at least one uppercase letter."
        )

    if not re.search(
        r"[a-z]",
        password
    ):

        return (
            False,
            "Password must contain at least one lowercase letter."
        )

    if not re.search(
        r"[0-9]",
        password
    ):

        return (
            False,
            "Password must contain at least one number."
        )

    return (
        True,
        "Password is valid."
    )


# =====================================================
# SIGN UP
# =====================================================

def signup_user(
    name: str,
    email: str,
    password: str
):

    name = name.strip()
    email = email.strip().lower()

    # -----------------------------------------------
    # Validate Name
    # -----------------------------------------------

    if not name:

        return (
            False,
            "Please enter your name."
        )

    # -----------------------------------------------
    # Validate Email
    # -----------------------------------------------

    if not is_valid_email(
        email
    ):

        return (
            False,
            "Please enter a valid email address."
        )

    # -----------------------------------------------
    # Validate Password
    # -----------------------------------------------

    valid, message = validate_password(
        password
    )

    if not valid:

        return (
            False,
            message
        )

    # -----------------------------------------------
    # Check Existing User
    # -----------------------------------------------

    existing_user = users_collection.find_one(
        {
            "email": email
        }
    )

    if existing_user:

        return (
            False,
            "An account with this email already exists."
        )

    # -----------------------------------------------
    # Hash Password
    # -----------------------------------------------

    hashed_password = hash_password(
        password
    )

    # -----------------------------------------------
    # Create User
    # -----------------------------------------------

    user = {

        "name": name,

        "email": email,

        "password": hashed_password,

        "created_at": datetime.now(
            timezone.utc
        ),

        "reset_token": None,

        "reset_token_expiry": None
    }

    users_collection.insert_one(
        user
    )

    return (
        True,
        "Account created successfully."
    )


# =====================================================
# LOGIN
# =====================================================

def login_user(
    email: str,
    password: str
):

    email = email.strip().lower()

    user = users_collection.find_one(
        {
            "email": email
        }
    )

    if not user:

        return (
            False,
            "Invalid email or password.",
            None
        )

    password_correct = verify_password(
        password,
        user["password"]
    )

    if not password_correct:

        return (
            False,
            "Invalid email or password.",
            None
        )

    # -----------------------------------------------
    # Return Safe User Information
    # -----------------------------------------------

    safe_user = {

        "id": str(
            user["_id"]
        ),

        "name": user["name"],

        "email": user["email"]
    }

    return (
        True,
        "Login successful.",
        safe_user
    )


# =====================================================
# CREATE PASSWORD RESET TOKEN
# =====================================================

def create_reset_token(
    email: str
):

    email = email.strip().lower()

    user = users_collection.find_one(
        {
            "email": email
        }
    )

    if not user:

        return (
            False,
            "No account found with this email address.",
            None
        )

    # -----------------------------------------------
    # Generate Secure Random Token
    # -----------------------------------------------

    token = secrets.token_urlsafe(
        32
    )

    expiry = (
        datetime.now(
            timezone.utc
        )
        + timedelta(
            minutes=15
        )
    )

    users_collection.update_one(

        {
            "_id": user["_id"]
        },

        {
            "$set": {

                "reset_token": token,

                "reset_token_expiry": expiry
            }
        }
    )

    return (
        True,
        "Password reset token created.",
        token
    )


# =====================================================
# RESET PASSWORD
# =====================================================

def reset_password(
    token: str,
    new_password: str
):

    user = users_collection.find_one(
        {
            "reset_token": token
        }
    )

    if not user:

        return (
            False,
            "Invalid or expired reset token."
        )

    expiry = user.get(
        "reset_token_expiry"
    )

    if not expiry:

        return (
            False,
            "Invalid or expired reset token."
        )

    # -----------------------------------------------
    # Check Expiry
    # -----------------------------------------------

    now = datetime.now(
        timezone.utc
    )

    if expiry < now:

        users_collection.update_one(

            {
                "_id": user["_id"]
            },

            {
                "$set": {

                    "reset_token": None,

                    "reset_token_expiry": None
                }
            }
        )

        return (
            False,
            "Reset token has expired."
        )

    # -----------------------------------------------
    # Validate New Password
    # -----------------------------------------------

    valid, message = validate_password(
        new_password
    )

    if not valid:

        return (
            False,
            message
        )

    # -----------------------------------------------
    # Hash New Password
    # -----------------------------------------------

    new_hashed_password = hash_password(
        new_password
    )

    # -----------------------------------------------
    # Update Password
    # -----------------------------------------------

    users_collection.update_one(

        {
            "_id": user["_id"]
        },

        {
            "$set": {

                "password": new_hashed_password,

                "reset_token": None,

                "reset_token_expiry": None
            }
        }
    )

    return (
        True,
        "Password reset successfully."
    )


# =====================================================
# LOGOUT
# =====================================================

def logout_user():

    return True