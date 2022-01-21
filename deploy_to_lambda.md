# To deploy an updated lambda function to AWS Lambda
1) Create package. Detailed instructions can be found in the AWS docs [here](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html).


# Deploy to Lambda function
Package libraries and execution code into a zip file and deploy to AWS Lambda
`./deploy_to_lambda.sh`

# Architecture
KEMA is an event-driven architecture that utilizes Lambda functions to send and process SMS messages. Briefly, an incoming SMS message will be ingested by Twilio. This message is redirected to an API endpoint in AWS API Gateway. The endpoint triggers a Lambda function checks for existing conversation threads for that user phone numbers and reroutes the message based on the result.

More information on how to set up Lambda functions on AWS can be found [here](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html). More information on how to set up API endpoints that trigger Lambda functions can be found [here](https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python-amazon-lambda).

- The lambder_handler function is located within the lambda_function.py file. This is The default lambda function name and location in, so make sure to specify the file name and function name if this changed.
