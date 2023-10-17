import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')  

def create_historical_data_table():
    historical_data_table = dynamodb.create_table(
        TableName='HistoricalData',
        KeySchema=[
            {
                'AttributeName': 'PrimaryKey',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'PrimaryKey',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5 #change lol
        }
    )

    historical_data_table.meta.client.get_waiter('table_exists').wait(TableName='HistoricalData')
    print("HistoricalData table created successfully!")



if __name__ == '__main__':
    try:
        create_historical_data_table()
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("HistoricalData table already exists.")
    except Exception as e:
        print(f"Error creating HistoricalData table: {e}")