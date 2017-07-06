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

    def generate_message_to_trigger_build(
            self, ref='refs/heads/test--test-1.0'):
        return self.generate_message_from_sns(
                {
                    'after': 'commit-hash',
                    'ref': ref
                })

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
        return {
            'builds': [
                {
                    'buildStatus': 'test-status',
                    'sourceVersion': 'test-version',
                    'id': 'test-id',
                }
            ]
        }

    @patch('app.sleep')
    @patch('lib.codebuild_wrapper._get_buildspec_override')
    @patch('app.load_source_code_to_s3')
    @patch('lib.codebuild_wrapper.codebuild_client.start_build')
    def test_correct_setup_for_test__build_is_triggered(
            self, start_build_mock, 
            load_source_code_to_s3_mock, 
            get_buildspec_override_mock, sleep_mock):
        """
        Test that we trigger CodeBuild build
        with valid parameters
        """
        # disable side effects
        sleep_mock.return_value = None
        get_buildspec_override_mock.side_effect = \
            lambda lambda_name, file_name: file_name
        load_source_code_to_s3_mock.side_effect = \
            lambda github_ref: github_ref

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
            ],
            buildspecOverride='buildspec-test')

    @patch('app.sleep')
    @patch('lib.codebuild_wrapper._get_buildspec_override')
    @patch('app.load_source_code_to_s3')
    @patch('lib.codebuild_wrapper.codebuild_client.start_build')
    def test_correct_setup_for_build__build_is_triggered(
            self, start_build_mock, 
            load_source_code_to_s3_mock, 
            get_buildspec_override_mock, sleep_mock):
        """
        Test that we trigger CodeBuild build
        with valid parameters
        """
        # disable side effects
        sleep_mock.return_value = None
        get_buildspec_override_mock.side_effect = \
            lambda lambda_name, file_name: file_name
        load_source_code_to_s3_mock.side_effect = \
            lambda github_ref: github_ref

        start_build_mock.return_value = ''
        response = handler(
            self.generate_message_to_trigger_build(
                ref='refs/tags/test--1.1'), {})
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
            ],
            buildspecOverride='buildspec-build')

    @patch('lib.s3_wrapper.s3_client.upload_file')
    @patch('lib.github_wrapper.github.Github')
    def test_load_source_code_to_s3(
            self, github_mock, upload_file_mock):
        """
        Test api usage in load_source_code_to_s3
        function
        """
        # arrange os variables
        import os
        os.environ['SOURCE_CODE_S3_BUCKET'] = 's3-bucket'
        os.environ['SOURCE_CODE_S3_KEY'] = 's3-key'

        # set up mocks
        github_mock.return_value.\
            get_repo.return_value.get_archive_link.return_value = 'test-github-url'
        upload_file_mock.return_value = {
            'VersionId': 'test-s3'}

        from lib.s3_wrapper import load_source_code_to_s3

        version_id = load_source_code_to_s3('test-ref')

        self.assertEqual(
            version_id, 'test-s3')
        upload_file_mock.assert_called_with(
            'test-github-url', 's3-bucket', 's3-key')
        github_mock.return_value.\
            get_repo.return_value.get_archive_link.\
                assert_called_with('zip', ref='test-ref')


    @patch('app.sleep')
    @patch('lib.codebuild_wrapper._get_buildspec_override')
    @patch('app.load_source_code_to_s3')
    @patch('lib.codebuild_wrapper.codebuild_client.start_build')
    def test_load_source_code_to_s3_usage(
            self, start_build_mock,
            load_source_code_to_s3_mock,
            get_buildspec_override_mock,
            sleep_mock):
        """
        Test that we pass correct data to load_source_code_to_s3
        method
        """
        # disable side effects
        sleep_mock.return_value = None
        get_buildspec_override_mock.side_effect = \
            lambda lambda_name, file_name: file_name
        load_source_code_to_s3_mock.side_effect = \
            lambda github_ref: github_ref

        start_build_mock.return_value = ''
        response = handler(
            self.generate_message_to_trigger_build(
                ref='refs/tags/test--1.1'), {})
        load_source_code_to_s3_mock.assert_called_with(
            'commit-hash')

    @patch('app.sleep')
    @patch('lib.result.set_status_to_github')
    @patch('lib.result.codebuild_client.batch_get_builds')
    def test_correct_setup__result_is_set(
            self, batch_get_build_mock, set_status_to_github_mock, sleep_mock):
        """
        Test that we use github api correctly
        """
        # disable side effects
        sleep_mock.return_value = None
        set_status_to_github_mock.return_value = ''
        batch_get_build_mock.return_value = \
            self.generate_batch_build_return_value()

        response = handler(
            self.generate_message_to_set_github_results(), {})
        self.assertEqual(
            response['statusCode'], HTTP_200_OK)
        batch_get_build_mock.assert_called_with(ids=['1'])  

 
    @patch('app.sleep')
    @patch('lib.github_wrapper.github')
    @patch('lib.result.get_build_status')   
    def test_correct_setup__build_status_is_queried_correctly(
            self, get_build_status, github, sleep_mock):
        """
        Test that we request build status with correct parameters
        """
        # disable side effects
        sleep_mock.return_value = None
        # prepare mocks
        get_build_status.return_value = \
            self.generate_batch_build_return_value()['builds'][0]
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
