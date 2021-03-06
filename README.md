## CodeBuild with pull request builder

This will build out all the resources needed to use
[AWS codebuild](https://aws.amazon.com/codebuild/) and integrate
with a github to make a pull request builder.

When a commit is pushed to github.  Github sends a SNS message
which then invokes the Lambda. The lambda will update github
via the status api and set the status to pending. The last step
of codebuild will invoke the lambda again to report the build result.

AWS SNS integration is managed by CloudFormation template.

![Data flow](https://github.com/holvi-anastasiia/pull-request-builder/blob/master/ci-schema.jpeg)

## Setup

### Requirements

### Github Oauth token
Neccessary scopes:
- admin:repo_hook
- repo

### Package lambda to ```dist/deployment.zip```
*The file name is hardcoded in cloudformation template*

TODO: automate this
```
$ mkdir -p dist
$ pip install -r lambda/requirements.txt -t ./dist
$ cp -r lambda/lib ./dist
$ cp lambda/app.py ./dist
$ cd dist && zip -r deployment.zip *
```

#### ENV Varialbes

```
$ export GITHUB_PROJECT_NAME='tatums/hello-world'
$ export GITHUB_TOKEN='1234567890'
$ export PROJECT_NAME='foo-bar'
```
#### AWS Cli

This relies on the [aws cli](https://aws.amazon.com/cli/). Make sure you're setup

#### [Setup resources](./resources/README.md)
```bash
$ ./resources/create
```

This will create the following resources in AWS
*Names for recourses will be equal to stack project name*

* *CodeBuild Project*

Docker image: aws/codebuild/eb-python-3.4-amazonlinux-64:2.1.6

Source: github, project with github project name from parameter variables

No artifacts

* *SNS Topic*

* *Lambda*
Uses package from dist/deployment.zip
Runtime: pythin 2.7
Set up env variables used in code:
- GITHUB_LAMBDAS_REPO
- GITHUB_OAUTH
- PROJECT_NAME

* *IAM user with keys* (for the github integration)
Policy allow publish to sns topic

Extra Roles created:
1) Lambda: create logs
2) CodeBuild: access to logs 

### Deploy the lambda
```
$ cd lambda
$ npm install && npm run deploy
```


### Setup Github's Amazon SNS integration
In the github project, setup the service/integration `Amazon SNS` and provide the required info.

You can pull the info using a script `$ ./resources/find_keys`

![github setup](./gh-setup.png "Github integration setup")

### in your project you'll need to setup a `buildspec.yml` file.

[CodeBuild buildspec docs](http://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html)

Notice that you'll need to trigger a SNS call in the post_build step.


```YAML
version: 0.1

environment_variables:
  plaintext:
    SNS_TOPIC_ARN: arn:aws:sns:us-east-1:012345678902:pull-request-builder

phases:
  install:
    commands:
      - echo Nothing to do in the install phase...
  pre_build:
    commands:
      - npm install
  build:
    commands:
      - echo Build started on `date`
      - npm test
  post_build:
    commands:
      - echo Build completed on `date`
      - 'aws sns publish --topic-arn arn:aws:sns:us-east-1:012345678902:pull-request-builder --message "{\"buildId\": \"$CODEBUILD_BUILD_ID\"}"'
```
