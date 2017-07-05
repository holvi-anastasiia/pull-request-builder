YAML_CONFIG = """version: 0.2

env:
  variables:
    LAMBDA: "default"
    SNS_TOPIC_ARN: arn:aws:sns:eu-west-1:890057277545:LambdaDeployPipeline
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
      - 'mkdir -p dist'
      - 'chalice package dist'
      - 'aws lambda update-function-code --function-name $LAMBDA --zip-file fileb://dist/deployment.zip'
  post_build:
    commands:
      - 'aws sns publish --topic-arn arn:aws:sns:eu-west-1:890057277545:LambdaDeployPipeline --message "{\\"buildId\\": \\"$CODEBUILD_BUILD_ID\\"}"'"""