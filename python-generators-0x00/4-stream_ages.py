#!/usr/bin/python3
"""
Module that provides functions to calculate the average age of users
in a memory-efficient way using generators
"""
import mysql.connector


def stream_user_ages():
    """
    Generator function that yields user ages one by one
    
    Yields:
        int: Age of a user
    """
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Execute query to get only the ages
        cursor.execute("SELECT age FROM user_data")
        
        # Yield each age one by one
        for (age,) in cursor:
            yield age
            
        # Clean up
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def calculate_average_age():
    """
    Calculates the average age without loading the entire dataset into memory
    
    Returns:
        float: Average age of users
    """
    total_age = 0
    count = 0
    
    # Use the generator to stream ages one by one
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    # Calculate and return the average age
    if count > 0:
        average_age = total_age / count
        print(f"Average age of users: {average_age:.2f}")
        return average_age
    else:
        print("No users found")
        return 0


if __name__ == "__main__":
    calculate_average_age()
