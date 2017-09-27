# Seattle Garbage Pickup
A simple API and app to find your next garbage, recycling and yard waste pickup days in Seattle.

# Garbage Pickup API

The `lambda_api` folder is a simple API that returns the next two months of garbage pickup information for
a specified Seattle street address.

# Deploying
## AWS Lambda function
Note: this assumes you have `aws` command line set up with correct permissions to push!
1. From the `lambda_api` folder, zip everything into a package to be uploaded: `zip -r /tmp/lambda_package.zip *`
2. Upload your package: `aws lambda update-function-code --function-name [arn] --zip-file fileb:///tmp/lambda_package.zip`
3. Profit!
4. Test? Should figure that out some day.
