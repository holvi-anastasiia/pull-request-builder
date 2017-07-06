YAML_CONFIG = """version: 0.2

env:
  variables:
    LAMBDA: "default"
    SNS_TOPIC_ARN: arn:aws:sns:eu-west-1:072560318001:test-ci-cd-with-codebuild-v3
    GITHUB_COMMIT: "default"
phases:
  install:
    commands:
      # find directory with source code
      # unfortunately github sends zipfile with inner dir
      - cd $(find . -name "holvi*" -type d | sed 1q)
      - ls -la
      - pip install -r requirements.txt
  pre_build:
    commands:
      - 'cd lambdas/$LAMBDA && pip install -r requirements.txt'
  build:
    commands:
      - 'coverage run --source=. -m unittest discover'
  post_build:
    commands:
      - 'aws sns publish --topic-arn arn:aws:sns:eu-west-1:072560318001:test-ci-cd-with-codebuild-v3 --message "{\\"buildId\\": \\"$CODEBUILD_BUILD_ID\\"}"'"""