from auth import users_collection

print("✅ MongoDB connection successful!")

print(
    "Database:",
    users_collection.database.name
)

print(
    "Collection:",
    users_collection.name
)