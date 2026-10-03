import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

print("Redis connection:", r.ping())

print("\nRedis keys:")

keys = r.keys("*")

if keys:
    for key in keys:
        print("-", key)
else:
    print("No keys currently stored.")