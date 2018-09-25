from botlog import BotLog
from botindicators import BotIndicators
from bottrade_new import BotTrade
import winsound
import pandas as pd
from Poloniex_new import Poloniex
polo = Poloniex('[API key]','[API secret]')

class BotStrategy(object):
    def __init__(self):
        self.output = BotLog()
        self.prices = []
        self.closes = [] # Needed for Momentum Indicator
        self.trades = []
        self.currentPrice = ""
        self.numSimulTrades = 1
        self.indicators = BotIndicators()
        self.type_trade = False
        self.GRC_bal = False
        self.BTC_bal = False
        self.Total_bal = False
        self.can_buy = False
        self.to_buy = False
        self.to_sell = False
        self.pair = 'BTC_GRC'
        self.order_num = False
        self.balance = False
        self.sell_price_last = False
        self.buy_price_last = False
        self.loss_break = 0
        self.orders = []
        self.high_bid_price = False
        self.low_ask_price = False
        self.low_ask_amount = False
        self.high_bid_amount = False
        self.price_to_buy = False
        self.price_to_sell = False
        self.short_MA_period = 12
        self.long_MA_period = 26
        self.signal_MA_period = 9
        self.winsound = winsound
        self.frequency = 2500  # Set Frequency To 2500 Hertz
        self.duration = 1000  # Set Duration To 1000 ms == 1 second
        self.short_EMA_list = []
        self.long_EMA_list = []
        self.MACD_list = []
        self.MACD_sig_list = []
        self.MACD_hist_list = []
        self.openTrades = []


    def tick(self,candlestick):
        self.currentPrice = float(candlestick.priceAverage)
        self.prices.append(self.currentPrice)
        self.update_MACD()
        self.output.log("Price: "+str(candlestick.priceAverage) +"  Short EMA: "+str(self.short_EMA_list[-1])+"  Long EMA: "+str(self.long_EMA_list[-1]))
        self.set_order_prices()
        self.evaluatePositions_MACD()


    def evaluatePositions_MACD(self):
        if len(self.prices) >= self.long_MA_period:
            self.updateOpenTrades()
            if len(self.prices) == self.long_MA_period:
                self.output.log('')
                self.output.log('***** FIRST ORDER POSSIBLE HERE *****')
                self.output.log('')

            if len(self.openTrades) < self.numSimulTrades:
                if self.MACD_hist_list[-2] <  self.MACD_hist_list[-1] < 0\
                        and self.BTC_bal > .0001\
                        and self.MACD_hist_list[-3] < 0 \
                        and self.MACD_list[-1] < -0.4e-8:
                    self.to_buy = self.can_buy
                    val_check = "Value check " + self.pair + " " + "{:.8f}".format(self.price_to_buy) + " " + "{:.8f}".format(self.to_buy)
                    self.output.log(val_check)
                    placed_order = polo.buy(self.pair, "{:.8f}".format(self.price_to_buy), "{:.8f}".format(self.to_buy))
                    self.output.log("Buy order placed!")
                    self.output.log(placed_order)
                    # self.winsound.Beep(self.frequency, self.duration)
                    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

                elif self.MACD_hist_list[-2] >  self.MACD_hist_list[-1] > 0\
                        and self.GRC_bal * float(self.currentPrice) > .0001\
                        and self.MACD_hist_list[-3] > 0 \
                        and self.MACD_list[-1] > 0.4e-08:
                    self.to_sell = self.GRC_bal
                    val_check = "Value check " + self.pair + " " + "{:.8f}".format(self.price_to_sell) + " " + "{:.8f}".format(self.to_sell)
                    self.output.log(val_check)
                    placed_order = polo.sell(self.pair, "{:.8f}".format(self.price_to_sell), "{:.8f}".format(self.to_sell))
                    self.output.log("Sell order placed!")
                    self.output.log(placed_order)
                    self.trades.append(BotTrade(self.order_num, self.currentPrice, self.type_trade, self.loss_break))
                    # self.winsound.Beep(self.frequency, self.duration)
                    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

    def Order_book(self, pair):
        orders = polo.returnOrderBook(pair, 1)
        self.high_bid_price = float(orders['bids'][0][0])
        self.high_bid_amount = float(orders['bids'][0][1])
        self.low_ask_price = float(orders['asks'][0][0])
        self.low_ask_amount = float(orders['asks'][0][1])


    def updateOpenTrades(self):
        self.openTrades = polo.returnOpenOrders(self.pair)
        if len(self.openTrades) > 0:
            self.output.log(self.openTrades)
            for trade in self.openTrades:
                order_Num = trade['orderNumber']
                order_Type = trade['type']
                if order_Type == "buy" \
                        and self.MACD_hist_list[-2] > self.MACD_hist_list[-1] > 0 \
                        and self.MACD_hist_list[-3] > 0 \
                        and self.MACD_list[-1] > 0.4e-08:
                    polo.cancelOrder(order_Num)
                    out_message = "Buy order closed"
                    self.output.log(out_message)
                elif order_Type == "sell" \
                        and self.MACD_hist_list[-2] < self.MACD_hist_list[-1] < 0 \
                        and self.MACD_hist_list[-3] < 0 \
                        and self.MACD_list[-1] < -0.4e-8:
                    self.to_buy = self.can_buy
                    polo.cancelOrder(order_Num)
                    out_message = "Sell order closed"
                    self.output.log(out_message)
            self.openTrades = polo.returnOpenOrders(self.pair)


    def update_MACD(self):
        prices_df = pd.DataFrame({'Prices': self.prices})
        short_ema_df = prices_df.ewm(span=self.short_MA_period).mean()
        long_ema_df = prices_df.ewm(span=self.long_MA_period).mean()
        self.short_EMA_list.append(short_ema_df.at[(len(self.prices) - 1), 'Prices'])
        self.long_EMA_list.append(long_ema_df.at[(len(self.prices) - 1), 'Prices'])

        MACD_current = self.short_EMA_list[-1] - self.long_EMA_list[-1]
        self.MACD_list.append(MACD_current)

        MACD_df = pd.DataFrame({'MACDs': self.MACD_list})
        MACD_sig_df = MACD_df.ewm(span=self.signal_MA_period).mean()
        self.MACD_sig_list.append(MACD_sig_df.at[(len(self.prices) - 1), 'MACDs'])

        MACD_hist_current = self.MACD_list[-1] - self.MACD_sig_list[-1]
        self.MACD_hist_list.append(MACD_hist_current)

        print('Current MACD = ' + str(self.MACD_list[-1]) + ' Current MACD sig = ' + str(self.MACD_sig_list[-1]) + ' Current MACD hist = ' + str(self.MACD_hist_list[-1]))


    def set_order_prices(self):
        self.balance = polo.returnBalances()
        self.GRC_bal = float(self.balance['GRC'])
        self.BTC_bal = float(self.balance['BTC'])
        self.Total_bal = self.GRC_bal + (self.BTC_bal / float(self.currentPrice))
        self.Order_book(self.pair)
        self.output.log("High bid: " + str(self.high_bid_price) + "Low ask: " + str(self.low_ask_price))
        if self.low_ask_price > float(self.currentPrice):
            if self.low_ask_amount > 1000:
                self.price_to_sell = self.low_ask_price - .00000001
            else:
                self.price_to_sell = self.low_ask_price
        elif self.low_ask_price == float(self.currentPrice):
            if self.low_ask_amount > 5000:
                self.price_to_sell = self.low_ask_price - .00000001
            else:
                self.price_to_sell = self.low_ask_price
        else:
            self.price_to_sell = float(self.currentPrice)

        if self.high_bid_price < float(self.currentPrice):
            if self.high_bid_amount > 1000:
                self.price_to_buy = self.high_bid_price + .00000001
            else:
                self.price_to_buy = self.high_bid_price
        elif self.high_bid_price == float(self.currentPrice):
            if self.high_bid_amount > 5000:
                self.price_to_buy = self.high_bid_price + .00000001
            else:
                self.price_to_buy = self.high_bid_price
        else:
            self.price_to_buy = float(self.currentPrice)
        self.can_buy = self.BTC_bal / self.price_to_buy

