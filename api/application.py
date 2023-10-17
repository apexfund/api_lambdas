from flask import Flask, jsonify, request
import boto3
import json
import threading, time
from boto3.dynamodb.conditions import Key


application = Flask(__name__)

lambda_client = boto3.client('lambda', region_name='us-west-2')
dynamodb = boto3.resource('dynamodb')
historical_data_table = dynamodb.Table('HistoricalData')

@application.route('/')
def hello():
    return jsonify({
        "message": "Historical Data API!",
        "endpoints": {
            "/historical_data": "fetch historical data for given tickers. Use POST with JSON body.",
            "/historical_data/<ticker>": "retrieve stored data for a specific ticker."
        }
    })

@application.route('/historical_data', methods=['GET', 'POST'])
def historical_data():
    if request.method == 'POST':
        data = request.json
        tickers = data.get('tickers', [])
        
        if not tickers:
            return jsonify({"error": "Please provide at least one ticker symbol in the 'tickers' list."}), 400
        
        tickers_str = ",".join(tickers)
        lambda_response = lambda_client.invoke(
            FunctionName="fetch_data",
            Payload=json.dumps({'tickers': tickers_str})
        )

        fetched_data = json.loads(lambda_response['Payload'].read())
        if not fetched_data:
            return jsonify({"error": "Failed to fetch data from Lambda function."}), 500
        
        process_lambda_response = lambda_client.invoke(
            FunctionName="process_data",
            Payload=json.dumps({
                'method': 'get_data',
                'data': json.dumps(fetched_data)
            })
        )

        processed_data = json.loads(process_lambda_response['Payload'].read())
        if processed_data.get('statusCode') != 200:
            return jsonify({"error": processed_data.get('body', 'Unknown error occurred while processing data.')}), 500
        
        return jsonify(fetched_data)
    else:
        # can change this so you can get data from dynamo ?.
        return jsonify({"message": "Use POST method to fetch and store data."})
    
@application.route('/historical_data/<ticker>', methods=['GET'])
def get_stored_data(ticker):
    response = historical_data_table.query(
        KeyConditionExpression=Key('ticker').eq(ticker)
    )
    items = response.get('Items', [])
    return jsonify(items)

def periodic_data_scrape():
    tickers = ["AAPL", "MSFT"]
    while True:
        for ticker in tickers:
            try:
                lambda_response = lambda_client.invoke(
                    FunctionName="fetch_data",
                    Payload=json.dumps({'tickers': ticker})
                )
                fetched_data = json.loads(lambda_response['Payload'].read())
                if fetched_data:
                    process_lambda_response = lambda_client.invoke(
                        FunctionName="process_data",
                        Payload=json.dumps({
                            'method': 'get_data',
                            'data': json.dumps(fetched_data)
                        })
                    )
            except Exception as e:
                print(f"Error fetching data for {ticker}: {str(e)}")
        # Gets data every day
        time.sleep(86400)

if __name__ == "__main__":
  #  threading.Thread(target=periodic_data_scrape, daemon=True).start()

    application.debug = True
    application.run()


