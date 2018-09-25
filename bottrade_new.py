import sys
from botlog import BotLog
import datetime
from Poloniex_new import Poloniex
polo = Poloniex('[API key]','[API secret')

class BotTrade(object):
    def __init__(self,order_num,currentPrice,type_trade,loss_break):
        self.output = BotLog()
        self.status = "OPEN"
        self.entryPrice = currentPrice
        self.exitPrice = ""
        self.output.log("Trade opened")
        self.type_trade = type_trade
        self.exit_time = False
        self.Order_num = order_num
        self.Loss_break = loss_break
        self.Balance = False
        self.GRC_bal = False
        self.BTC_bal = False
        self.pair = "BTC_GRC"
        self.out_amount = False

    def close(self,currentPrice):
        self.status = "CLOSED"
        self.exitPrice = currentPrice
        self.output.log("Trade closed")
        self.exit_time = datetime.datetime.now()
        polo.cancelOrder(self.Order_num)

    def tick(self, currentPrice):
        if currentPrice > self.Loss_break * 1.1:
            self.close(currentPrice)
            self.get_out(currentPrice)

    def get_out(self,currentPrice):
        self.Balance = polo.returnBalances()
        self.GRC_bal = float((self.Balance['GRC']))
        self.BTC_bal = float((self.Balance['BTC']))
        self.out_amount = self.BTC_bal / float(currentPrice)
        polo.buy(self.pair, currentPrice, self.out_amount)
        sys.exit()

    def showTrade(self):
        tradeStatus = "Order #: " + str(self.Order_num) +" Entry Price: "+str(self.entryPrice)+" Status: "+str(self.status)+" Exit Price: "+str(self.exitPrice) + " Trade Type " + str(self.type_trade)
        #+ " Exit Time: " + str(self.exit_time

        if (self.status == "CLOSED") and self.type_trade == "LONG":
            tradeStatus = tradeStatus + " Profit: "
            if (self.exitPrice > self.entryPrice):
                tradeStatus = tradeStatus + "\033[92m"
            else:
                tradeStatus = tradeStatus + "\033[91m"
            tradeStatus = tradeStatus+str(self.exitPrice - self.entryPrice)+"\033[0m"

        elif (self.status == "CLOSED") and self.type_trade == "SHORT":
            tradeStatus = tradeStatus + " Profit: "
            if (self.exitPrice < self.entryPrice):
                tradeStatus = tradeStatus + "\033[92m"
            else:
                tradeStatus = tradeStatus + "\033[91m"

            tradeStatus = tradeStatus+str(self.entryPrice - self.exitPrice)+"\033[0m"


        self.output.log(tradeStatus)
