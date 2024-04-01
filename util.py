import datetime
import pytz
from fyers_apiv3 import fyersModel
import time
from dotenv import load_dotenv
import os

load_dotenv()

iso_format="%Y-%m-%d %H:%M:%S"

PERatio= os.environ["PE_RATIO"]
gapThreshold= os.environ["GAP_THRESHOLD"]

fyers = fyersModel.FyersModel(client_id=os.environ['APP_ID'], token=os.environ['ACCESS_TOKEN'], log_path=os.getcwd())

def convertEpochToDateTimeFormat(_timestamp , _timezone):
    timestamp = datetime.datetime.fromtimestamp(_timestamp, tz=pytz.timezone(_timezone))
    timestamp = timestamp.strftime(iso_format)
    return timestamp

def isIndiaTradingHoursStarted(_timestamp):
    target_time = datetime.time(9, 15)  # Set the target time for comparison
    # Parse the timestamp string into a datetime object
    timestamp_dt = datetime.datetime.strptime(_timestamp, iso_format)

    # Extract the time component from the datetime object
    timestamp_time = timestamp_dt.time()

    if timestamp_time >= target_time:
        return True


def getHistoryData(_symbol,_from):
    fyers = fyersModel.FyersModel(client_id=os.environ['APP_ID'], token=os.environ['ACCESS_TOKEN'], log_path=os.getcwd())

    seconds = int(time.time()) + 19800
    seconds = str(seconds)
    data = {
        "symbol": _symbol,
        "resolution": "3",
        "date_format": "0",
        "range_from": _from,
        "range_to": seconds,
        "cont_flag": "1"
    }

    return fyers.history(data=data)

def ifInThreeMinuteArray(value):
    threeMinArray=["09:18", "09:21", "09:24", "09:27", "09:30", "09:33", "09:36", "09:39", "09:42", "09:45", "09:48", "09:51", "09:54", "09:57", "10:00", "10:03", "10:06", "10:09", "10:12", "10:15", "10:18", "10:21", "10:24", "10:27", "10:30", "10:33", "10:36", "10:39", "10:42", "10:45", "10:48", "10:51", "10:54", "10:57", "11:00", "11:03", "11:06", "11:09", "11:12", "11:15", "11:18", "11:21", "11:24", "11:27", "11:30", "11:33", "11:36", "11:39", "11:42", "11:45", "11:48", "11:51", "11:54", "11:57", "12:00", "12:03", "12:06", "12:09", "12:12", "12:15", "12:18", "12:21", "12:24", "12:27", "12:30", "12:33", "12:36", "12:39", "12:42", "12:45", "12:48", "12:51", "12:54", "12:57", "13:00", "13:03", "13:06", "13:09", "13:12", "13:15", "13:18", "13:21", "13:24", "13:27", "13:30", "13:33", "13:36", "13:39", "13:42", "13:45", "13:48", "13:51", "13:54", "13:57", "14:00", "14:03", "14:06", "14:09", "14:12", "14:15", "14:18", "14:21", "14:24", "14:27", "14:30", "14:33", "14:36", "14:39", "14:42", "14:45", "14:48", "14:51", "14:54", "14:57", "15:00", "15:03", "15:06", "15:09", "15:12", "15:15", "15:18", "15:21", "15:24", "15:27", "15:30"]
    if value in threeMinArray:
        return True
    else:
        return False
    

def checkForSellCondtion(last_column):
    PEstoploss=0
    PEtarget=0
    gap=0
    SellConditionAlert=False
    PEtriggerPoint=0
    if ((last_column['open'].item() > last_column['EMA'].item()) and (
            last_column['close'].item() > last_column['EMA'].item()) and (last_column['SUPERT'].item()==-1)):
        ##mark condition true as well populate triggerPoint,stoploss also add in proccessedAlert.
        SellConditionAlert = True
        PEstoploss = last_column['high'].item()
        if (last_column['open'].item() > last_column['close'].item()):
            PEtriggerPoint = last_column['low'].item()
            gap = PEstoploss - PEtriggerPoint
        
        else:
            PEtriggerPoint = last_column['open'].item()
            gap = PEstoploss - PEtriggerPoint
        
        if gap>gapThreshold:
            gap=gapThreshold
        PEtarget = PEtriggerPoint- (PERatio*gap)

    return {SellConditionAlert,gap,PEstoploss,PEtarget,PEtriggerPoint}


def checkForBuyCondtion(last_column):
    CEstoploss=0
    CEtarget=0
    gap=0
    BuyConditionAlert=False
    CEtriggerPoint=0
    if ((last_column['open'].item() < last_column['EMA'].item()) and (
            last_column['close'].item() < last_column['EMA'].item()) and (last_column['SUPERT'].item()==1)):
        ##mark condition true as well populate triggerPoint,stoploss also add in proccessedAlert.
        BuyConditionAlert = True
        CEstoploss = last_column['low'].item()
        if (last_column['open'].item() < last_column['close'].item()):
            CEtriggerPoint = last_column['high'].item()
            gap = CEtriggerPoint -CEstoploss
        
        else:
            CEtriggerPoint = last_column['open'].item()
            gap = CEtriggerPoint - CEstoploss
        
        if gap>gapThreshold:
            gap=gapThreshold
        CEtarget = CEtriggerPoint+(PERatio*gap)

    return {BuyConditionAlert,gap,CEstoploss,CEtarget,CEtriggerPoint}


def getCurrentExpirySymbol(_ltp , _optionType):
    strikePrice = int(round(_ltp / 100, 0) * 100)
    optionSymbol = os.environ["CURRENT_EXPIRY_SYMBOL"] + str(strikePrice) + _optionType
    return optionSymbol

def getQuotesData(_expirySymbolName):
    fyers = fyersModel.FyersModel(client_id=os.environ['APP_ID'], token=os.environ['ACCESS_TOKEN'],is_async=False ,log_path=os.getcwd())
    startTime = time.time()
    data = {
        "symbols": _expirySymbolName
    }
    responseOption = fyers.quotes(data=data)
    print(f"time taken to execute the getOption data is {time.time() - startTime} ms response {responseOption}")
    return responseOption

def placeOrder(_expirySymbolName,_orderType,_limitPrice,_optionType):
    fyers = fyersModel.FyersModel(client_id=os.environ['APP_ID'], token=os.environ['ACCESS_TOKEN'],is_async=False ,log_path=os.getcwd())

    _limitPrice= _limitPrice+1

    data = {
        "symbol":_expirySymbolName,
        "qty":50,
        "type":1,
        "side":1,
        "productType":"INTRADAY",
        "limitPrice":_limitPrice,
        "stopPrice":0,
        "validity":"DAY",
        "disclosedQty":0,
        "offlineOrder":False,
        "orderTag":"tag1"
    }

    response = fyers.place_order(data=data)
    
    if response['s'] == 'ok' and response['code']== 1101:
        order_id = response['id']
        print(f"Order placed successfully. Order ID:{order_id}")
        if (_optionType == "PE"):
            PEBuyorderId = _expirySymbolName+"-INTRADAY"
            isPEOrderPlaced = True
            return {isPEOrderPlaced,PEBuyorderId}
        else:
            CEBuyorderId = _expirySymbolName+"-INTRADAY"
            isCEOrderPlaced = True
            return {isCEOrderPlaced,CEBuyorderId}
    else:
        error_code = response['code']
        error_message = response['message']
        print(f"Order placement failed. Error:{error_message}")
        return {False , ""}


def exitPosition(_orderId , _orderType):
    fyers = fyersModel.FyersModel(client_id=os.environ['APP_ID'], token=os.environ['ACCESS_TOKEN'],is_async=False ,log_path=os.getcwd())

    data = {
        "id": str(_orderId)
    }

    response = fyers.exit_positions(data=data)

    print(response)
    if response['s'] == 'ok' and response['code']==200:
        print(f"order with orderId:{_orderId} exited successfully")
        if (_orderType == "PE"):
            isPEOrderPlaced = False
            return isPEOrderPlaced
        else:
            isCEOrderPlaced = False
            return isCEOrderPlaced
    else:
        print(f"error in exiting order with ID :{_orderId} and orderType:{_orderType}")
        return True


        
