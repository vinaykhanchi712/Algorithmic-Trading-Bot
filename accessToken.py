
from fyers_apiv3 import fyersModel
from dotenv import load_dotenv
import os

load_dotenv()


client_id= os.environ['APP_ID']
secret_key= "XXXXXXXX"
redirect_uri="https://trade.fyers.in/api-login/redirect-uri/index.html"
response_type="code"
grant_type="authorization_code"


auth_code= "your auth code here"

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type= response_type,
    grant_type=grant_type
    
)

session.set_token(auth_code)
response= session.generate_token()

print(response)