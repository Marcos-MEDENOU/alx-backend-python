#!/usr/bin/env python3
"""Test cases for the utils module.

This module contains unit tests for the utility functions defined in utils.py.
"""
import unittest
from typing import Any, Dict, Tuple, Union, Mapping, Sequence
from unittest.mock import Mock, patch

from .utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test class for the access_nested_map function.
    
    This class tests various scenarios for accessing nested dictionary
    structures using a sequence of keys.
    """
    
    def test_access_nested_map(self) -> None:
        """Test that access_nested_map returns the expected result."""
        test_cases = [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ]
        
        for nested_map, path, expected in test_cases:
            with self.subTest(nested_map=nested_map, path=path, expected=expected):
                self.assertEqual(access_nested_map(nested_map, path), expected)
    
    def test_access_nested_map_exception(self) -> None:
        """Test that access_nested_map raises KeyError for invalid paths."""
        test_cases = [
            ({}, ("a",), "a"),
            ({"a": 1}, ("a", "b"), "b"),
        ]
        
        for nested_map, path, expected_key in test_cases:
            with self.subTest(nested_map=nested_map, path=path, expected_key=expected_key):
                with self.assertRaises(KeyError) as context:
                    access_nested_map(nested_map, path)
                self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Test class for the get_json function.
    
    This class tests the get_json function's ability to make HTTP requests
    and return the JSON response, using mocking to avoid actual HTTP calls.
    """
    
    def test_get_json(self) -> None:
        """Test that get_json returns the expected result."""
        test_cases = [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
        
        for test_url, test_payload in test_cases:
            with self.subTest(test_url=test_url, test_payload=test_payload):
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