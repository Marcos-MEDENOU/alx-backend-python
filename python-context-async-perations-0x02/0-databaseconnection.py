import sqlite3

class DatabaseConnection:
    """Custom class-based context manager for database connections"""
    
    def __init__(self, db_name='users.db'):
        """Initialize with database name"""
        self.db_name = db_name
        self.connection = None
    
    def __enter__(self):
        """Open database connection when entering the context"""
        print(f"Opening connection to {self.db_name}")
        self.connection = sqlite3.connect(self.db_name)
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Close database connection when exiting the context"""
        if self.connection:
            if exc_type is not None:
                # If an exception occurred, rollback any uncommitted changes
                print(f"Exception occurred: {exc_value}")
                self.connection.rollback()
            else:
                # If no exception, commit any pending changes
                self.connection.commit()
            
            print(f"Closing connection to {self.db_name}")
            self.connection.close()
        
        # Return False to propagate any exceptions
        return False

# Using the context manager with the 'with' statement
with DatabaseConnection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    
    print("Query results:")
    for row in results:
        print(row)