YAML_CONFIG = """version: 0.2

env:
  variables:
    LAMBDA: "default"
    SNS_TOPIC_ARN: arn:aws:sns:eu-west-1:072560318001:test-lambda-ci-cd
phases:
  install:
    commands:
      - pip install -r requirements.txt
  pre_build:
    commands:
      - 'cd lambdas/$LAMBDA && pip install -r requirements.txt'
  build:
    commands:
      - 'coverage run --source=. -m unittest discover'
  post_build:
    commands:
      - 'aws sns publish --topic-arn arn:aws:sns:eu-west-1:072560318001:test-lambda-ci-cd --message "{\\"buildId\\": \\"$CODEBUILD_BUILD_ID\\"}"'"""