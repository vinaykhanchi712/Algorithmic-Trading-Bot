import pandas as pd
from dotenv import load_dotenv
import os
import time
import util
import pandas as pd
import pandas_ta as pa

load_dotenv()

dataFrame = pd.DataFrame(columns=['timestamp', 'symbol', 'open', 'high', 'low', 'close'])
processedTimeStamp = []
previousTick = {'timestamp': 0, 'symbol': 0, 'open': 0, 'high': 0, 'low': 0, 'close': 0}
currentTick = {}
gOpen = 0
gHigh = 0
gLow = 100000000
gClose = 0
appendedOldData=False
PEOrderPlaced=False
CEOrderPlaced=False
processedAlertRows = []
SellCondition=False
BuyCondition=False
PEstoploss=0
CEstoploss=0
PEtarget=0
CEtarget=0
gap=0
PEtriggerPoint=0
CEtriggerPoint=0
PEorderId=""
CEOrderId=""
PNL = pd.DataFrame()

def startTrading(_timestamp,_symbol,_ltp):
    global appendedOldData ,dataFrame,PEOrderPlaced,CEOrderPlaced,processedAlertRows,SellCondition,BuyCondition
    global PEtriggerPoint,CEtriggerPoint,PEstoploss,CEstoploss,PEtarget,CEtarget,gap

    print("TIMESTAMP[{}] ltp of the symbol: {} is: {} ", _timestamp  , _symbol , _ltp)
    if appendedOldData==False:
        appendingPreviousMonthsData()
        appendedOldData=True
    print("DataFrame is : {}",dataFrame)
    processTickDataToGivenDataFrame(_timestamp,_symbol,_ltp,3)

    ##now data frame is ready. We need to apply our strategy.
    last_column = dataFrame.tail(1)
    if(PEOrderPlaced==True or CEOrderPlaced==True):
        postOrderPlacementHandling(last_column,_ltp,_timestamp,_symbol)
    else:
        if(SellCondition==True or BuyCondition==True):
            postAlertConditionHandling(last_column)
        else:
            if last_column['timestamp'].item() not in processedAlertRows:
                SellCondition,gap,PEstoploss,PEtarget,PEtriggerPoint=util.checkForSellCondtion(last_column)
                ##it is an optimisation that buy and sell can not occur together so we will not move to buy if sell condition is there.
                if SellCondition==False:
                    BuyCondition,gap,CEstoploss,CEtarget,CEtriggerPoint=util.checkForBuyCondtion(last_column)
                processedAlertRows.append(last_column['timestamp'].item())


def postOrderPlacementHandling(_last_column,_ltp,_timestamp,_symbol):
    global PEstoploss,PEorderId,CEOrderId,gap,PEtarget,PEtriggerPoint,PNL,PEOrderPlaced,CEOrderPlaced
    global CEstoploss,CEstoploss,CEtarget,CEtriggerPoint
    
    if (PEOrderPlaced == True):
        ##exit conditions for PE order
        if (_ltp >= PEstoploss):
            ##exit from trade and mark isOrderPlaced False
            temp = {"timestamp": _timestamp, "symbol": _symbol, "type": "PE", "price to exit": _ltp,
                    "sold at": PEtriggerPoint,
                    "reason": "SL hit", "profit/Loss": PEtriggerPoint - PEstoploss}
            PNL = PNL.append(temp, ignore_index=True)
            PEOrderPlaced=util.exitPosition(PEorderId,"PE")
            
        elif (_ltp <= (PEtarget)):
            PEstoploss = PEtarget + (gap/2)
            PEtarget = PEtarget - gap

    if (CEOrderPlaced == True):
        ##exit condition for CE order
        if (_ltp <= CEstoploss):
            temp = {"timestamp": _timestamp, "symbol": _symbol, "type": "CE", "price to exit": _ltp,
                    "placed at": CEtriggerPoint,
                    "reason": "SL hit", "profit/Loss": CEstoploss - CEtriggerPoint}
            PNL = PNL.append(temp, ignore_index=True)
            CEOrderPlaced=util.exitPosition(CEOrderId,"CE")
            
        elif(_ltp >= (CEtarget)):
            CEstoploss= CEtarget - (gap/2)
            CEtarget= CEtarget+gap



def postAlertConditionHandling(_last_column,_ltp ,_symbol,_timestamp):
    global SellCondition,PEstoploss,PEtriggerPoint,PEtarget,CEstoploss,CEtarget,CEtriggerPoint,PEOrderPlaced,CEOrderPlaced
    global PEorderId,CEOrderId,BuyCondition

    if (SellCondition == True):
        if (_ltp >= PEstoploss):
            SellCondition = False
        elif (_ltp < PEtriggerPoint):

            ##get strike price PE.
            expirySymbolName = util.getCurrentExpirySymbol(_ltp, "PE")
            responseOption= util.getQuotesData(expirySymbolName)
            
            ##place order
            PEOrderPlaced,PEorderId=util.placeOrder(expirySymbolName, "buy",responseOption["d"][0]["v"]["ask"],"PE")
            
            ## if order placed then make sell condition false
            if PEOrderPlaced==True:
                SellCondition=False
            


    if (BuyCondition == True):
        if (_ltp <= CEstoploss):
            BuyCondition = False
        elif (_ltp > CEtriggerPoint):

            ##get strike price CE.
            expirySymbolName = util.getCurrentExpirySymbol(_ltp, "CE")
            responseOption= util.getQuotesData(expirySymbolName)

            ## place order
            CEOrderPlaced,CEOrderId =util.placeOrder(expirySymbolName, "buy" , responseOption["d"][0]["v"]["bid"],"CE")
        
            ## if order placed then make buy condition false
            if CEOrderPlaced==True:
                BuyCondition=False



def processTickDataToGivenDataFrame(_timestamp,_symbol,_ltp,_timeFrame):
    global dataFrame,processedTimeStamp,previousTick,current_tick,gOpen,gHigh,gLow,gClose

    hour = _timestamp[11:13]
    min= _timestamp[14:16]
    second= _timestamp[17:19]
    acceptibleLagSeconds= ["00" ,"01" ,"02" ,"03" ,"04" ,"05", "06"]
    hourMinConcat = hour+":"+min
    if(util.ifInThreeMinuteArray(hourMinConcat) and ( second in acceptibleLagSeconds)):
        ## add to dataFrame
        if _timestamp[:17] not in processedTimeStamp:
            processedTimeStamp.append(_timestamp[:17])
            ### changing timestamp to mark as previous time candle.
            previousMinute= int(_timeFrame[14:16]) - _timeFrame
            previousTick['timestamp'] = _timestamp[:15] + str(previousMinute)+ ':00'
            #print(f"[data to be added in data frame is] ,{previous_tick}")
            ###previousTickFrame= pd.DataFrame(previousTick)
            ###_dataFrame=pd.concat(_dataFrame,previousTickFrame,ignore_index=True)
            dataFrame = dataFrame.append(previousTick, ignore_index=True)
            dataFrame['timestamp'] = pd.to_datetime(dataFrame['timestamp'])
            dataFrame = dataFrame.set_index(dataFrame['timestamp'])

            dataFrame['EMA'] = pa.ema(dataFrame['close'], length=5)
            dataFrame['SUPERT'] = pa.supertrend(dataFrame['high'],dataFrame['low'],dataFrame['close'],length=10 , multiplier=2.5)['SUPERTd_10_2.5.0']

        gOpen = gHigh = gLow = gClose = _ltp
        currentTick = {'timestamp': _timestamp, 'symbol': _symbol, 'open': gOpen, 'high': gHigh, 'low': gLow,
                        'close': gClose}


    else:
        if (gOpen == 0):
            gOpen = _ltp
        gHigh = max(_ltp, gHigh)
        gLow = min(_ltp, gLow)
        gClose = _ltp
        currentTick = {'timestamp': _timestamp, 'symbol': _symbol, 'open': gOpen, 'high': gHigh, 'low': gLow,
                        'close': gClose}
    # print(f"current data is : ,{current_tick}")
    previousTick = currentTick


def appendingPreviousMonthsData():
    global dataFrame
    currentEpochTime = time.time()
    seconds_in_month = 30 * 24 * 60 * 60
    fromRange = currentEpochTime-seconds_in_month+19800
    fromRange=1702879118
    response = util.getHistoryData(os.environ['SYMBOL_NAME'], str(fromRange))
    print(f'TEST response is :{response}')
    if response['s'] == 'ok':
        for x in response['candles']:
            timestamp = util.convertEpochToDateTimeFormat(x[0],"Asia/Calcutta")
            temp = {'timestamp': timestamp, 'open': x[1], 'high': x[2], 'low': x[3], 'close': x[4]}
            dataFrame= dataFrame.append(temp,ignore_index=True)

    dataFrame['timestamp'] = pd.to_datetime(dataFrame['timestamp'])
    dataFrame = dataFrame.set_index(dataFrame['timestamp'])

    dataFrame['EMA'] = pa.ema(dataFrame['close'], length=5)
    dataFrame['SUPERT'] = pa.supertrend(dataFrame['high'],dataFrame['low'],dataFrame['close'],length=10 , multiplier=2.5)['SUPERTd_10_2.5.0']