import sqlite3

class ExecuteQuery:
    """Reusable context manager for executing database queries"""
    
    def __init__(self, query, parameters=None, db_name='users.db'):
        """
        Initialize the context manager with query and parameters
        
        Args:
            query (str): SQL query to execute
            parameters (tuple): Parameters for the query (optional)
            db_name (str): Database name (default: 'users.db')
        """
        self.query = query
        self.parameters = parameters or ()
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Open connection, execute query, and return results
        """
        print(f"Opening connection to {self.db_name}")
        
        # Open database connection
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        
        # Execute the query with parameters
        print(f"Executing query: {self.query}")
        if self.parameters:
            print(f"With parameters: {self.parameters}")
            self.cursor.execute(self.query, self.parameters)
        else:
            self.cursor.execute(self.query)
        
        # Fetch results
        self.results = self.cursor.fetchall()
        print(f"Query executed successfully, {len(self.results)} rows returned")
        
        # Return the results
        return self.results
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Clean up resources when exiting the context
        """
        if self.cursor:
            self.cursor.close()
        
        if self.connection:
            if exc_type is not None:
                # If an exception occurred, rollback any changes
                print(f"Exception occurred: {exc_value}")
                self.connection.rollback()
            else:
                # If no exception, commit any changes
                self.connection.commit()
            
            print(f"Closing connection to {self.db_name}")
            self.connection.close()
        
        # Return False to propagate any exceptions
        return False

# Using the ExecuteQuery context manager
with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as results:
    print("Users older than 25:")
    for row in results:
        print(row)

print("\n" + "="*50 + "\n")

# Another example - fetching all users
with ExecuteQuery("SELECT * FROM users") as results:
    print("All users:")
    for row in results:
        print(row)