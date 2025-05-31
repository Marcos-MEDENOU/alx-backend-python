#!/usr/bin/env python3
"""Test cases for the utils module.

This module contains unit tests for the utility functions defined in utils.py.
"""
import unittest
from typing import Any, Dict, Tuple, Union
from parameterized import parameterized
from unittest.mock import patch, Mock

from .utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test class for the access_nested_map function.
    
    This class tests various scenarios for accessing nested dictionary
    structures using a sequence of keys.
    """
    
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...],
        expected: Union[int, Dict[str, int]]
    ) -> None:
        """Test that access_nested_map returns the expected result.
        
        Args:
            nested_map: A nested dictionary to test with
            path: A tuple of keys representing the path to access
            expected: The expected value at the given path
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)
    
    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...],
        expected_key: str
    ) -> None:
        """Test that access_nested_map raises KeyError with expected message.
        
        Args:
            nested_map: A dictionary to test with
            path: A tuple of keys representing an invalid path
            expected_key: The key that should be in the error message
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Test class for the get_json function.
    
    This class tests the get_json function's ability to make HTTP requests
    and return the JSON response, using mocking to avoid actual HTTP calls.
    """
    
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(
        self,
        test_url: str,
        test_payload: Dict[str, Any]
    ) -> None:
        """Test that get_json returns the expected result.
        
        Args:
            test_url: The URL to test with
            test_payload: The expected JSON payload to be returned
        """
        # Create a mock response object with a json method that returns test_payload
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        
        # Patch requests.get to return our mock response
        with patch('requests.get', return_value=mock_response) as mock_get:
            # Call the function with the test URL
            result = get_json(test_url)
            
            # Verify that requests.get was called exactly once with test_url
            mock_get.assert_called_once_with(test_url)
            
            # Verify that the result matches test_payload
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test class for the memoize decorator.
    
    This class tests that the memoize decorator correctly caches the result
    of a method call and only calls the underlying method once.
    """
    
    def test_memoize(self) -> None:
        """Test that memoize caches the result of a method call."""
        # Define the test class inside the test method
        class TestClass:
            """Test class with a method to be memoized."""
            
            def a_method(self) -> int:
                """Return a fixed value for testing."""
                return 42
            
            @memoize
            def a_property(self) -> int:
                """Memoized property that calls a_method."""
                return self.a_method()
        
        # Create an instance of the test class
        test_obj = TestClass()
        
        # Patch the a_method to track calls and return a fixed value
        with patch.object(
            test_obj, 'a_method', return_value=42
        ) as mock_method:
            # First call - should call a_method
            result1 = test_obj.a_property
            # Second call - should use cached result
            result2 = test_obj.a_property
            
            # Verify the results are correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            
            # Verify a_method was only called once
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()