import boto3
import json

dynamodb = boto3.resource('dynamodb')
historical_data_table = dynamodb.Table('HistoricalData')

def store_data_for_tickers(ticker_data):
    with historical_data_table.batch_writer() as batch:
        for ticker, data in ticker_data.items():
            # historical price data
            for record in data['history']:
                primary_key = f"{ticker}#history#{record['Date']}"
                item = {
                    'PrimaryKey': primary_key,
                    'ticker': ticker,
                    'date': record['Date'],
                    'open': record['Open'],
                    'high': record['High'],
                    'low': record['Low'],
                    'close': record['Close'],
                    'volume': record['Volume'],
                    'type': 'history'
                }
                batch.put_item(Item=item)

            # dividends
            for date, value in data['dividends'].items():
                primary_key = f"{ticker}#dividend#{date}"
                item = {
                    'PrimaryKey': primary_key,
                    'ticker': ticker,
                    'date': date,
                    'dividend': value,
                    'type': 'dividend'
                }
                batch.put_item(Item=item)

            # splits
            for date, value in data['splits'].items():
                primary_key = f"{ticker}#split#{date}"
                item = {
                    'PrimaryKey': primary_key,
                    'ticker': ticker,
                    'date': date,
                    'split': value,
                    'type': 'split'
                }
                batch.put_item(Item=item)

            # Storing actions (dividends, splits)
            for record in data['actions'].to_dict(orient="records"):
                primary_key = f"{ticker}#action#{record['Date']}"
                item = {
                    'PrimaryKey': primary_key,
                    'ticker': ticker,
                    'date': record['Date'],
                    'dividends': record.get('Dividends', None),
                    'splits': record.get('Stock Splits', None),
                    'type': 'action'
                }
                batch.put_item(Item=item)

            # earnings dates
            for record in data['earnings_dates']:
                primary_key = f"{ticker}#earnings_date#{record['Date']}"
                item = {
                    'PrimaryKey': primary_key,
                    'ticker': ticker,
                    'date': record['Date'],
                    'type': 'earnings_date'
                }
                batch.put_item(Item=item)

            # income statements 
            for record in data['income_stmt'].to_dict(orient="records"):
                primary_key = f"{ticker}#income_stmt#{record['Date']}"
                item = {
                    'PrimaryKey': primary_key,
                    'ticker': ticker,
                    'date': record['Date'],
                    'revenue': record['Revenue'],
                    'netIncome': record['Net Income'],
                    'type': 'income_stmt'
                }
                batch.put_item(Item=item)

        


def process_data(event, context):
    method = event['method']
    data = json.loads(event['data'])

    try:
        if method == "get_data":
            store_data_for_tickers(data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return {
            'statusCode': 200,
            'body': 'Data processed and stored successfully!'
        }

    except Exception as e:
        print(str(e))
        return {
            'statusCode': 500,
            'body': 'An error occurred while processing data.'
        }
