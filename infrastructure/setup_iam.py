import boto3
import json
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')

def create_lambda_dynamodb_role():
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    dynamodb_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:BatchWriteItem",
                    "dynamodb:GetItem",
                    "dynamodb:Scan",
                    "dynamodb:Query",
                    "dynamodb:UpdateItem",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            }
        ]
    }

    role_name = "LambdaDynamoDBRole"

    role = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Role for Lambda to access DynamoDB"
    )

    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName="DynamoDBAccessPolicy",
        PolicyDocument=json.dumps(dynamodb_policy)
    )

    print(f"Role {role_name} created successfully with DynamoDB access!")


if __name__ == '__main__':
    try:
        create_lambda_dynamodb_role()
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("LambdaDynamoDBRole already exists.")
        else:
            print(f"Error creating LambdaDynamoDBRole: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
