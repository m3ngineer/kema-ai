# To deploy an updated lambda function to AWS Lambda
1) Upload
`mkdir lambda-deploy-pkg
cp lambda_function.py lambda-deploy-pkg/lambda_function.py
cp schedule.py lambda-deploy-pkg/schedule.py
cp conf.py lambda-deploy-pkg/conf.py
cp -R awslambda-psycopg2/psycopg2-3.7 lambda-deploy-pkg/psycopg2
cd lambda-deploy-pkg
zip -r ../lambda-deploy-pkg.zip .
cd ..
zip -g lambda-deploy-pkg.zip lambda_function.py schedule.py conf.py
`

# Deploy to function
`aws lambda update-function-code --function-name kema_text_buddy --zip-file fileb://lambda-deploy-pkg.zip
`


# Clean up directory
`rm -R lambda-deploy-pkg
rm -R lambda-deploy-pkg.zip
`
