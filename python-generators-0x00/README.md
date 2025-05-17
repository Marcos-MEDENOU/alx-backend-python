# Python Generators Project

This project demonstrates the use of Python generators to stream rows from an SQL database one by one.

## Files

- `seed.py`: Script to set up and populate the MySQL database
- `user_data.csv`: Sample data for the database
- `0-main.py`: Test script to verify the database setup

## Requirements

- Python 3
- MySQL server
- mysql-connector-python package

## Setup

1. Install the required package:
   ```
   pip install mysql-connector-python
   ```

2. Make sure MySQL server is running with appropriate credentials (default: user=root, password=root)

3. Run the test script:
   ```
   python 0-main.py
   ```

## Functions

- `connect_db()`: Connects to the MySQL database server
- `create_database(connection)`: Creates the database ALX_prodev if it does not exist
- `connect_to_prodev()`: Connects to the ALX_prodev database in MySQL
- `create_table(connection)`: Creates a table user_data if it does not exist with the required fields
- `insert_data(connection, data)`: Inserts data in the database if it does not exist
