from redis_client import (
    test_redis_connection,
    create_login_session,
    check_login_session,
    delete_login_session,
    save_reset_token,
    get_reset_token_email,
    delete_reset_token
)


print("=" * 50)
print("BOOK RAG - REDIS TEST")
print("=" * 50)


# ----------------------------------------------------
# 1. Redis Connection
# ----------------------------------------------------

if test_redis_connection():

    print("✅ Redis connection successful!")

else:

    print("❌ Redis connection failed!")

    exit()


# ----------------------------------------------------
# 2. Login Session
# ----------------------------------------------------

test_email = "test@example.com"

print("\nTesting login session...")

create_login_session(test_email)

if check_login_session(test_email):

    print("✅ Login session created successfully!")

else:

    print("❌ Login session was NOT created!")


# ----------------------------------------------------
# 3. Logout / Delete Session
# ----------------------------------------------------

print("\nTesting logout session deletion...")

delete_login_session(test_email)

if not check_login_session(test_email):

    print("✅ Login session deleted successfully!")

else:

    print("❌ Login session was NOT deleted!")


# ----------------------------------------------------
# 4. Reset Password Token
# ----------------------------------------------------

test_token = "test-reset-token-123"

print("\nTesting reset token...")

save_reset_token(
    test_token,
    test_email
)

saved_email = get_reset_token_email(
    test_token
)

if saved_email == test_email:

    print("✅ Reset token saved successfully!")

else:

    print("❌ Reset token was NOT saved correctly!")


# ----------------------------------------------------
# 5. Delete Reset Token
# ----------------------------------------------------

print("\nTesting reset token deletion...")

delete_reset_token(
    test_token
)

deleted_email = get_reset_token_email(
    test_token
)

if deleted_email is None:

    print("✅ Reset token deleted successfully!")

else:

    print("❌ Reset token was NOT deleted!")


print("\n" + "=" * 50)
print("REDIS TEST COMPLETED")
print("=" * 50)