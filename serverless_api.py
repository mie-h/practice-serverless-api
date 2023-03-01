from fastapi import FastAPI, HTTPException, status
import json

app = FastAPI()


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

def build_response():
    pass


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health")
def get_health():
    return 


@app.get("/product/{id}")
def get_product(id: int):
    try:
        response = table.get_item(
            Key={
                'productId': id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Error message: {e}")

    if 'Item' in response:
        return build_response(200, response['Item'])
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item with id: {id} was not found")


@app.get("/products")
def get_products():
    pass


@app.post("/product")
def post_product():
    pass


@app.patch("/product")
def update_product():
    pass


@app.delete("/delete")
def delete_product():
    pass