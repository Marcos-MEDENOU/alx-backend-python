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

def transactional(func):
    """Decorator that manages database transactions"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Start transaction (SQLite is in autocommit mode by default)
            # Begin transaction by executing a statement
            conn.execute("BEGIN")
            
            # Execute the original function
            result = func(conn, *args, **kwargs)
            
            # If successful, commit the transaction
            conn.commit()
            return result
            
        except Exception as e:
            # If an error occurs, rollback the transaction
            conn.rollback()
            # Re-raise the exception to preserve the original error
            raise e
    
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

#### Update user's email with automatic transaction handling 
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')