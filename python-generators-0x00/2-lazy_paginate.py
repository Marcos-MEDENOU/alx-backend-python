#!/usr/bin/python3
"""
Module that provides a generator function for lazy pagination of user data
"""
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetches a page of users from the database
    
    Args:
        page_size (int): Number of rows to fetch in each page
        offset (int): Starting position for fetching rows
        
    Returns:
        List of dictionaries, each representing a row from the database
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator function that implements lazy loading of paginated data
    
    Args:
        page_size (int): Number of rows to fetch in each page
        
    Yields:
        List of dictionaries, each representing a page of data
    """
    offset = 0
    
    # This is the only loop in the function
    while True:
        # Get the next page of data
        page = paginate_users(page_size, offset)
        
        # If no more data, stop iteration
        if not page:
            break
            
        # Yield the page
        yield page
        
        # Update offset for next page
        offset += page_size
