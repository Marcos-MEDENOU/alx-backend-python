#!/usr/bin/env python3
""" Test client functions
"""
import unittest
from client import GithubOrgClient
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock
from utils import get_json
import fixtures
from unittest.mock import patch


class TestGithubOrgClient(unittest.TestCase):
    """ Class to test GithubOrgClient class
    """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, input, mock_get_json):
        """ Test org method
        """
        url = "https://api.github.com/orgs/{}".format(input)
        mock_get_json.return_value = {"login": input}
        client = GithubOrgClient(input)
        self.assertRaises(TypeError, client.org)
        mock_get_json.assert_called_once()

    @patch('client.get_json')
    def test_public_repos_url(self, mock_get_json):
        """ Test that the _public_repos_url method returns the correct value
        """
        url = "http://example.com"
        mock_get_json.return_value = {"repos_url": url}
        client = GithubOrgClient("google")
        self.assertEqual(client._public_repos_url, url)
        mock_get_json.assert_called_once()

    @patch('client.get_json')
    @patch(
        'client.GithubOrgClient._public_repos_url',
        new_callable=PropertyMock
    )
    def test_public_repos(self, mock_public_repos_url, mock_get_json):
        """ Test that the public_repos method returns the correct value
        """
        mock_payload = [
            {"name": "repo1", "license": {"key": "test"}},
            {"name": "repo2"},
        ]
        mock_get_json.return_value = mock_payload
        mock_public_repos_url.return_value = "http://example.com"
        client = GithubOrgClient("google")
        repos = client.public_repos()
        mock_get_json.assert_called_once()
        mock_public_repos_url.assert_called_once()
        self.assertEqual(repos, ["repo1", "repo2"])
        self.assertEqual(client.public_repos("notFound"), [])
        repos = client.public_repos("test")
        self.assertEqual(repos, ["repo1"])

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """ Test that the has_license method returns the correct value
        """
        client = GithubOrgClient("google")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class(
    # get the parameters from the fixtures module
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    fixtures.TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """ Class to test integration of GithubOrgClient class
    """
    @classmethod
    def setUpClass(cls):
        """ Set up for all methods
        """
        # patch get_json to return the expected payload
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        # set the side effect to return the expected payload
        cls.mock_get.return_value.json.side_effect = [
            cls.org_payload, cls.repos_payload
        ]

    @classmethod
    def tearDownClass(cls):
        """ Clean up after all methods
        """
        # stop the patcher
        cls.get_patcher.stop()

    def test_public_repos(self):
        """ Test public_repos method
        """
        client = GithubOrgClient("google")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """ Test public_repos method with license
        """
        client = GithubOrgClient("google")
        repos = client.public_repos("apache-2.0")
        self.assertEqual(repos, self.apache_repos)



if __name__ == "__main__":
    unittest.main()
