import time
import sqlite3 
import functools

def with_db_connection(func):
    """Decorator that automatically handles database connections"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection, even if an exception occurs
            conn.close()
    
    return wrapper

query_cache = {}

def cache_query(func):
    """Decorator that caches query results based on SQL query string"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        query = None
        
        # Check if query is passed as positional argument (after conn)
        if len(args) > 1:
            query = args[1]  # First arg is conn, second is typically query
        # Check if query is passed as keyword argument
        elif 'query' in kwargs:
            query = kwargs['query']
        
        # If we found a query, check cache
        if query:
            # Use the query string as cache key
            cache_key = query.strip().lower()  # Normalize the query for consistent caching
            
            # Check if result is already cached
            if cache_key in query_cache:
                print(f"Cache hit for query: {query}")
                return query_cache[cache_key]
            
            # Execute the function if not cached
            print(f"Cache miss for query: {query}")
            result = func(*args, **kwargs)
            
            # Store result in cache
            query_cache[cache_key] = result
            print(f"Result cached for query: {query}")
            return result
        
        # If no query found, execute without caching
        return func(*args, **kwargs)
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")