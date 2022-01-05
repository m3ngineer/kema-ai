# To deploy an updated lambda function to AWS Lambda
1) Create package. Detailed instructions can be found in the AWS docs [here](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html).
`
rm -R lambda-deploy-pkg
rm -R lambda-deploy-pkg.zip
mkdir lambda-deploy-pkg
cp lambda_function.py lambda-deploy-pkg/lambda_function.py
cp lambda_function_reminder.py lambda-deploy-pkg/lambda_function_reminder.py
cp schedule.py lambda-deploy-pkg/schedule.py
cp db.py lambda-deploy-pkg/db.py
cp reminder.py lambda-deploy-pkg/reminder.py
cp conf.py lambda-deploy-pkg/conf.py
cp -R awslambda-psycopg2/psycopg2-3.7 lambda-deploy-pkg/psycopg2
cp -R twilio lambda-deploy-pkg/twilio
cd lambda-deploy-pkg
zip -r ../lambda-deploy-pkg.zip .
cd ..
zip -g lambda-deploy-pkg.zip lambda_function.py schedule.py conf.py
`

# Deploy to Lambda function
`aws lambda update-function-code --function-name kema_text_buddy --zip-file fileb://lambda-deploy-pkg.zip
`

# Clean up directory
`rm -R lambda-deploy-pkg
rm -R lambda-deploy-pkg.zip
`

# Create a Lambda Function
https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

- The lambder_handler function is located within the lambda_function.py file. This is The default lambda function name and location in, so make sure to specify the file name and function name if this changed.

# Link to API Gateway
https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python-amazon-lambda
