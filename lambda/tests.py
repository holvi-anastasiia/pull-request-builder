"""
Smoke tests for github lambda
"""
import json
from mock import patch, MagicMock
import unittest

from app import handler


HTTP_200_OK = 200


class PullRequestBuilderSmokeTest(unittest.TestCase):

    def setUp(self):
        # set up environmenty variables
        import os
        os.environ['PROJECT'] = 'test'
        os.environ['GITHUB_OAUTH'] = 'test-oauth'
        os.environ['GITHUB_LAMBDAS_REPO'] = 'test-repo'
        os.environ['AWS_REGION'] = 'test-region'

    def generate_message_to_trigger_build(self):
        return self.generate_message_from_sns(
                {'after': 'commit-hash'})

    def generate_message_to_set_github_results(self):
        return self.generate_message_from_sns(
                {'buildId': '1'})

    def generate_message_from_sns(self, message):
        return {
            'Records': [
                {
                    'Sns': {
                        'Message': json.dumps(message)
                    }
                }
            ]
        }

    def generate_batch_build_return_value(self):
        return [
            {
                'buildStatus': 'test-status',
                'sourceVersion': 'test-version',
                'id': 'test-id',
            }
        ]

    @patch('lib.build.codebuild_client.start_build')
    def test_correct_setup__build_is_triggered(
            self, start_build_mock):
        """
        Test that we trigger CodeBuild build
        with valid parameters
        """
        start_build_mock.return_value = ''
        response = handler(
            self.generate_message_to_trigger_build(), {})
        self.assertEqual(
            response['statusCode'], HTTP_200_OK)
        start_build_mock.assert_called_with(
            projectName='test',
            sourceVersion='commit-hash',
            environmentVariablesOverride=[
                {
                    'name': 'LAMBDA',
                    # TODO: get lambda value on the flight
                    'value': 'test',
                } 
            ])

    @patch('lib.result.set_status_to_github')
    @patch('lib.result.codebuild_client.batch_get_builds')
    def test_correct_setup__result_is_set(
            self, batch_get_build_mock, set_status_to_github_mock):
        """
        Test that we use github api correctly
        """
        set_status_to_github_mock.return_value = ''
        batch_get_build_mock.return_value = \
            self.generate_batch_build_return_value()

        response = handler(
            self.generate_message_to_set_github_results(), {})
        self.assertEqual(
            response['statusCode'], HTTP_200_OK)
        batch_get_build_mock.assert_called_with(ids=['1'])  

 
    @patch('lib.status.github')
    @patch('lib.result.get_build_status')   
    def test_correct_setup__build_status_is_queried_correctly(
            self, get_build_status, github):
        """
        Test that we request build status with correct parameters
        """
        # prepare mocks
        get_build_status.return_value = \
            self.generate_batch_build_return_value()[0]
        github.Github.return_value = MagicMock()
        github.Github.return_value.get_repo.return_value.\
            get_commit.return_value.create_status.return_value = ''
        response = handler(
            self.generate_message_to_set_github_results(), {})
        self.assertEqual(
            response['statusCode'], HTTP_200_OK)
        # verify github behaviour
        github.Github.return_value.get_repo.return_value.\
            get_commit.return_value.create_status.assert_called_with(
                'pending',
                'https://console.aws.amazon.com/codebuild/home?region=test-region#/builds/test-id/view/new',
                'test-status')
        github.Github.return_value.get_repo.\
            return_value.get_commit.assert_called_with('test-version')


if __name__ == '__main__':
    unittest.main()
