
from fyers_api import accessToken
from dotenv import load_dotenv
import os

load_dotenv()

client_id= os.environ['APP_ID']
secret_key= "XXXXXXXXX"
redirect_uri="https://google.com"
response_type="code"
state= "sample_state"

session = accessToken.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type= response_type
    
)


response= session.generate_authcode()

print(response)