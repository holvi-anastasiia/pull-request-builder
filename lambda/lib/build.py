"""
Start CodeBuild building
"""
import os

import boto3


codebuild_client = boto3.client('codebuild')


def trigger_build(source_version):
	"""
	Trigger build for given source_version

	Assumes that  we have PROJECT environment variable set
	"""
	# return codebuild response for debug
	return codebuild_client.start_build(
		projectName=os.environ['PROJECT'],
		sourceVersion=source_version,
		environmentVariablesOverride=[
            {
                'name': 'LAMBDA',
                # TODO: get lambda value on the flight
                'value': 'test',
            } 
		])
		# TODO: override buildspec
		# according to build type (test or build)
