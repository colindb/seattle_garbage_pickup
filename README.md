# Seattle Garbage Pickup
A simple API and app to find your next garbage, recycling and yard waste pickup days in Seattle.

# Deploying
Note: this assumes you have `aws` command line set up with correct permissions to push!
1. From the `lambda_skill` folder, zip everything into a package to be uploaded: `zip -r /tmp/lambda_skill.zip *`
2. Upload your package: `aws lambda update-function-code --function-name [arn] --zip-file fileb:///tmp/lambda_skill.zip`
3. Profit!
4. Test? Should figure that out some day.

# Testing
The `test_lambda.py` file can be used to do some basic sanity testing after pushing to AWS: `python3 test_lambda.py`