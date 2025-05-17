#!/usr/bin/python3
"""
Seed script for setting up MySQL database with user data
and streaming rows using generators
"""
import csv
import mysql.connector
import uuid
import os


def connect_db():
    """
    Connects to the MySQL database server
    Returns: MySQL connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
        print("Database ALX_prodev created successfully")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL
    Returns: MySQL connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None


def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL,
                INDEX (user_id)
            )
        """)
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")


def insert_data(connection, csv_file):
    """
    Inserts data in the database if it does not exist
    Args:
        connection: MySQL connection object
        csv_file: Path to the CSV file containing user data
    """
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Data already exists in the table. Skipping insertion.")
            cursor.close()
            return
        
        # Get absolute path to the CSV file
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, csv_file)
        
        # Read data from CSV and insert into the table
        with open(csv_path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            
            for row in csv_reader:
                # Check if we have enough columns
                if len(row) >= 4:
                    # Use provided UUID or generate a new one
                    user_id = row[0] if len(row[0]) == 36 else str(uuid.uuid4())
                    name = row[1]
                    email = row[2]
                    age = row[3]
                    
                    cursor.execute(
                        "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                        (user_id, name, email, age)
                    )
        
        connection.commit()
        cursor.close()
        print(f"Data from {csv_path} inserted successfully")
    except FileNotFoundError:
        print(f"Error: CSV file {csv_path} not found")
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")


def stream_rows(connection, table_name, batch_size=5):
    """
    Generator function that streams rows from a database table one by one
    
    Args:
        connection: MySQL connection object
        table_name: Name of the table to stream data from
        batch_size: Number of rows to fetch at a time (default: 5)
        
    Yields:
        One row at a time from the database
    """
    try:
        cursor = connection.cursor(dictionary=True)
        offset = 0
        
        while True:
            # Fetch a batch of rows
            query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # If no more rows, stop iteration
            if not rows:
                break
                
            # Yield each row one by one
            for row in rows:
                yield row
                
            # Update offset for next batch
            offset += batch_size
            
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error streaming data: {err}")
        yield None
