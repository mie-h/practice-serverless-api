from fastapi import FastAPI, HTTPException, status
import json
import boto3
import os
from dotenv import load_dotenv, find_dotenv
from Item import Item, PatchItem
from custom_encoder import CustomEncoder
from mangum import Mangum

load_dotenv(find_dotenv())

app = FastAPI()
lambda_handler = Mangum(app)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

dynamodb_table_name = 'product-inventory'
dynamodb = boto3.resource('dynamodb', 
                          region_name='us-west-1')
table = dynamodb.Table(dynamodb_table_name)


def build_response(status_code, body=None):
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Contral-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health")
def get_health():
    return build_response(200)


@app.get("/product/{id}")
def get_product(id: int):
    try:
        response = table.get_item(
            Key={
                'productId': id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error message: {e}")

    if 'Item' in response:
        return build_response(200, response['Item'])
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item with id: {id} was not found")


@app.get("/products")
def get_products():
    try:
        response = table.scan()
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        
        body = {
            'products': data
        }
        return build_response(200, body)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error message: {e}")


# curl -X POST 'http://127.0.0.1:8000/product' -d '{"productId":1002, "color":"blue", "price":200}' -H "Content-Type: application/json"
@app.post("/product")
def save_product(item: Item):
    try:
        item_dict = item.dict()
        table.put_item(Item=item_dict)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': item_dict
        }
        return build_response(200, body)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error message: {e}")


# curl -X PATCH 'http://127.0.0.1:8000/product' -d '{"productId":1002, "key":"color", "value":"orange"}' -H "Content-Type: application/json"
@app.patch("/product")
def update_product(item: PatchItem):
    item_dict = item.dict()
    try:
        response = table.update_item(
            Key={
                'productId': item_dict['productId']
            },
            UpdateExpression='set %s = :value' % item_dict['key'],
            ExpressionAttributeValues={
                ':value': item_dict['value']
            },
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return build_response(200, body)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error message: {e}")


@app.delete("/product/{id}")
def delete_product(id: int):
    try:
        response = table.delete_item(
            Key={
                'productId': id
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return build_response(200, body)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error message: {e}")

