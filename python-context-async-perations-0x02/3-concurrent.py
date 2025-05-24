import asyncio
import aiosqlite
import time


async def async_fetch_users():
    """
    Asynchronously fetch all users from the database
    """
    print("Starting to fetch all users...")
    start_time = time.time()
    
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        await cursor.close()
    
    end_time = time.time()
    print(f"Fetched {len(results)} users in {end_time - start_time:.2f} seconds")
    return results


async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database
    """
    print("Starting to fetch users older than 40...")
    start_time = time.time()
    
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        results = await cursor.fetchall()
        await cursor.close()
    
    end_time = time.time()
    print(f"Fetched {len(results)} users older than 40 in {end_time - start_time:.2f} seconds")
    return results


async def fetch_concurrently():
    """
    Execute both database queries concurrently using asyncio.gather
    """
    print("Starting concurrent database queries...")
    start_time = time.time()
    
    # Execute both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    end_time = time.time()
    print(f"\nConcurrent execution completed in {end_time - start_time:.2f} seconds")
    
    # Display results
    print(f"\n--- All Users ({len(all_users)} total) ---")
    for user in all_users[:5]:  # Show first 5 users
        print(user)
    if len(all_users) > 5:
        print(f"... and {len(all_users) - 5} more users")
    
    print(f"\n--- Users Older Than 40 ({len(older_users)} total) ---")
    for user in older_users:
        print(user)
    
    return all_users, older_users


async def create_sample_data():
    """
    Create sample data for demonstration (optional)
    """
    async with aiosqlite.connect('users.db') as db:
        # Create table if it doesn't exist
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT
            )
        ''')
        
        # Insert sample d