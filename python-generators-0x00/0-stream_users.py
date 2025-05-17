#!/usr/bin/python3
"""
Module that provides a generator function to stream users from a database
"""
import mysql.connector


def stream_users():
    """
    Generator function that streams rows from the user_data table one by one
    
    Yields:
        One row at a time from the database as a dictionary
    """
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        
        # Create a cursor that returns dictionaries
        cursor = connection.cursor(dictionary=True)
        
        # Execute query to get all users
        cursor.execute("SELECT * FROM user_data")
        
        # Yield each row one by one - this is the only loop in the function
        for row in cursor:
            yield row
            
        # Clean up (this code runs after the generator is exhausted)
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
