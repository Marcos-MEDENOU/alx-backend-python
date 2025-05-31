#!/usr/bin/env python3
"""Unit tests for client module.
"""
import unittest
from unittest.mock import patch
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
        test_payload = {"repos_url": "https://api.github.com/orgs/test/repos"}
        mock_get_json.return_value = test_payload
        
        client = GithubOrgClient(org_name)
        result = client.org
        
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected URL."""
        test_payload = {
            "repos_url": "https://api.github.com/orgs/test/repos"
        }
        
        with patch('client.GithubOrgClient.org',
                   new_callable=lambda: test_payload) as mock_org:
            client = GithubOrgClient("test")
            result = client._public_repos_url
            
            self.assertEqual(result, test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the expected list of repos."""
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = test_repos_payload
        
        test_repos_url = "https://api.github.com/orgs/test/repos"
        
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=lambda: test_repos_url) as mock_repos_url:
            client = GithubOrgClient("test")
            result = client.public_repos()
            
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            
            mock_get_json.assert_called_once_with(test_repos_url)
            mock_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns the expected boolean value."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test cases for GithubOrgClient class.
    """

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures and start mocking requests.get."""
        def mock_requests_get(url):
            """Mock function to return appropriate payloads based on URL."""
            class MockResponse:
                def json(self):
                    if "orgs/" in url and not url.endswith("/repos"):
                        # This is an organization URL
                        return cls.org_payload
                    elif url.endswith("/repos"):
                        # This is a repos URL
                        return cls.repos_payload
                    else:
                        return {}
            
            return MockResponse()
        
        # Start the patcher for requests.get
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.side_effect = mock_requests_get

    @classmethod
    def tearDownClass(cls):
        """Clean up class fixtures and stop mocking."""
        cls.get_patcher.stop()


if __name__ == '__main__':
    unittest.main()