#!/usr/bin/python3
"""
Module that provides functions to stream and process user data in batches
"""
import mysql.connector


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows in batches from the user_data table
    
    Args:
        batch_size (int): Number of rows to fetch in each batch
        
    Yields:
        List of dictionaries, each representing a row from the database
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
        
        # Get total number of rows
        cursor.execute("SELECT COUNT(*) as count FROM user_data")
        total_rows = cursor.fetchone()['count']
        
        # Process in batches
        offset = 0
        while offset < total_rows:
            # Execute query to get a batch of users
            cursor.execute(f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}")
            batch = cursor.fetchall()
            
            # If no more rows, break the loop
            if not batch:
                break
                
            # Yield the batch
            yield batch
            
            # Update offset for next batch
            offset += batch_size
        
        # Clean up
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25
    
    Args:
        batch_size (int): Number of rows to fetch in each batch
    """
    # Stream users in batches
    for batch in stream_users_in_batches(batch_size):
        # Process each user in the batch
        for user in batch:
            # Filter users over the age of 25
            if user['age'] > 25:
                # Print the user with a blank line after each user for readability
                print(user)
                print()
