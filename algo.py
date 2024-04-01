from fyers_apiv3.FyersWebsocket import data_ws
from dotenv import load_dotenv
import os
import util
import tradingFramework

load_dotenv()

def onmessage(message):
    """
    Callback function to handle incoming messages from the FyersDataSocket WebSocket.

    Parameters:
        message (dict): The received message from the WebSocket.

    """
    print("TEST LOG : message received is :{}",message)
    timestamp= util.convertEpochToDateTimeFormat(message["exch_feed_time"], "Asia/Calcutta")
    print("TIMESTAMP[{}] ltp of the symbol: {} is: {} ", timestamp  , message["symbol"] , message["ltp"])

    


    if util.isIndiaTradingHoursStarted(timestamp):
        tradingFramework.startTrading(timestamp,message["symbol"] , message["ltp"])
    else:
        print("The time is not after 9:15 yet.")
    
    
def onerror(message):
    """
    Callback function to handle WebSocket errors.

    Parameters:
        message (dict): The error message received from the WebSocket.


    """
    print("Error:", message)


def onclose(message):
    """
    Callback function to handle WebSocket connection close events.
    """
    print("Connection closed:", message)


def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.

    """
    # Specify the data type and symbols you want to subscribe to
    data_type = "SymbolUpdate"

    # Subscribe to the specified symbols and data type
    symbols = [os.environ['SYMBOL_NAME']]
    fyers.subscribe(symbols=symbols, data_type=data_type)

    # Keep the socket running to receive real-time data
    fyers.keep_running()


# Replace the sample access token with your actual access token obtained from Fyers
access_token = os.environ['ACCESS_TOKEN']
app_id = os.environ['APP_ID']


# Create a FyersDataSocket instance with the provided parameters
fyers = data_ws.FyersDataSocket(
    access_token= (str)(app_id+":"+access_token),       # Access token in the format "appid:accesstoken"
    log_path="./logs",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=False,                  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,              # Save response in a log file instead of printing it.
    reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,               # Callback function to subscribe to data upon connection.
    on_close=onclose,                # Callback function to handle WebSocket connection close events.
    on_error=onerror,                # Callback function to handle WebSocket errors.
    on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
)

# Establish a connection to the Fyers WebSocket
fyers.connect()

      
 
