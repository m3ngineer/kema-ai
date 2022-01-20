mkdir lambda-deploy-pkg
cp lambda_function.py lambda-deploy-pkg/lambda_function.py
cp lambda_function_reminder.py lambda-deploy-pkg/lambda_function_reminder.py
cp schedule.py lambda-deploy-pkg/schedule.py
cp message.py lambda-deploy-pkg/message.py
cp db.py lambda-deploy-pkg/db.py
cp reminder.py lambda-deploy-pkg/reminder.py
cp conf.py lambda-deploy-pkg/conf.py
cp -R awslambda-psycopg2/psycopg2-3.7 lambda-deploy-pkg/psycopg2
cp -R twilio lambda-deploy-pkg/twilio
cp -R pytz lambda-deploy-pkg/pytz
cd lambda-deploy-pkg
zip -r ../lambda-deploy-pkg.zip .
cd ..
zip -g lambda-deploy-pkg.zip lambda_function.py schedule.py conf.py

aws lambda update-function-code --function-name kema_text_buddy --zip-file fileb://lambda-deploy-pkg.zip
aws lambda update-function-code --function-name kema_send_reminder --zip-file fileb://lambda-deploy-pkg.zip

rm -R lambda-deploy-pkg
rm -R lambda-deploy-pkg.zip
