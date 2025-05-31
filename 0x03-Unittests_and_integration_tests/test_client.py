#!/usr/bin/env python3
"""Test cases for the GithubOrgClient class.

This module contains unit tests for the GithubOrgClient class, which interacts
with the GitHub API to fetch organization and repository information.
"""
import unittest
import sys
import os
from typing import Dict
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from 0x03-Unittests_and_integration_tests.client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for the GithubOrgClient class.
    
    This class tests the functionality of the GithubOrgClient methods,
    particularly focusing on the org property which fetches organization
    data from the GitHub API.
    """
    
    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json')
    def test_org(
        self,
        org_name: str,
        mock_get_json: Mock
    ) -> None:
        """Test that GithubOrgClient.org returns the correct value.
        
        This test verifies that:
        1. The org property returns the expected data
        2. get_json is called exactly once with the correct URL
        3. No actual HTTP request is made
        
        Args:
            org_name: The name of the organization to test with
            mock_get_json: The mocked get_json function
        """
        # Set up test data
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload
        
        # Create client instance and call the org property
        client = GithubOrgClient(org_name)
        result = client.org
        
        # Verify the result is as expected
        self.assertEqual(result, test_payload)
        
        # Verify get_json was called exactly once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        
        # Verify the result is cached (second call shouldn't call get_json again)
        _ = client.org
        mock_get_json.assert_called_once()


if __name__ == "__main__":
    unittest.main()
