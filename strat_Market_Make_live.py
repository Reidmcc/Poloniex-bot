from botlog import BotLog
from botindicators import BotIndicators
from bottrade_new import BotTrade
import winsound
import pandas as pd
from Poloniex_new import Poloniex
polo = Poloniex('[API key]','[API secret')

class BotStrategy(object):
    def __init__(self):
        self.output = BotLog()
        self.prices = []
        self.currentPrice = ""
        self.indicators = BotIndicators()
        self.GRC_bal = False
        self.BTC_bal = False
        self.Total_bal = False
        self.can_buy = False
        self.can_sell = False
        self.trade_amount = .00059 # BTC
        self.to_buy = False
        self.to_sell = False
        self.pair = 'BTC_GRC'
        self.order_num = False
        self.orders = []
        self.high_bid_price = False
        self.low_ask_price = False
        self.low_ask_amount = False
        self.high_bid_amount = False
        self.price_to_buy = False
        self.price_to_sell = False
        self.openTrades = []
        self.open_Bids = []
        self.open_Asks = []
        self.orders = []
        self.last_sell_price = False
        self.last_buy_price = False
        self.open_sell_flag = False
        self.open_buy_flag = False
        self.raw_spread = 0
        self.mod_spread = 0
        self.place_orders_flag = True


    def tick(self,candlestick):
        print('')
        print('############## Gridcoin data ###############')
        self.currentPrice = float(candlestick.priceAverage)
        self.prices.append(self.currentPrice)
        print("Price: "+str(candlestick.priceAverage))
        self.set_order_prices()
        self.updateOpenTrades()
        self.evaluatePositions_Market_Make()
        print('############## End Gridcoin data ###############')


    def evaluatePositions_Market_Make(self):
        # Have to re-check balances after possibly cancelling orders
        self.balance = polo.returnBalances()
        self.GRC_bal = float(self.balance['GRC'])
        self.BTC_bal = float(self.balance['BTC'])
        self.Total_bal = self.GRC_bal + (self.BTC_bal / float(self.currentPrice))

        if self.place_orders_flag == True:
        # Current code uses a BTC constant for trade amount, defined above

            if self.open_buy_flag == False:
                # self.can_buy = self.BTC_bal / self.price_to_buy
                if self.BTC_bal > 0.95 * self.trade_amount: #extra padding was to allow for FLDC trading
                    if self.BTC_bal > self.trade_amount:
                        self.to_buy = self.trade_amount / self.price_to_buy
                    else:
                         self.to_buy = self.BTC_bal * 0.99 / self.price_to_buy
                    val_check = "Value check " + self.pair + " " + "{:.8f}".format(self.price_to_buy) + " " + "{:.8f}".format(self.to_buy)
                    print(val_check)
                    placed_order = polo.buy(self.pair, "{:.8f}".format(self.price_to_buy), "{:.8f}".format(self.to_buy))
                    print("Buy order placed!")
                    print(placed_order)


            if self.open_sell_flag == False:
                if self.GRC_bal > self.trade_amount / self.price_to_sell * 0.95:
                    if self.GRC_bal > self.trade_amount / self.price_to_sell:
                         self.to_sell = self.trade_amount / self.price_to_sell
                    else:
                        self.to_sell = self.GRC_bal * 0.99
                    val_check = "Value check " + self.pair + " " + "{:.8f}".format(self.price_to_sell) + " " + "{:.8f}".format(self.to_sell)
                    print(val_check)
                    placed_order = polo.sell(self.pair, "{:.8f}".format(self.price_to_sell), "{:.8f}".format(self.to_sell))
                    print("Sell order placed!")
                    print(placed_order)

        # Code for trading with a GRC constant
        # if self.place_orders_flag == True:
        #
        #     if self.open_buy_flag == False:
        #         self.can_buy = self.BTC_bal / self.price_to_buy
        #         if self.can_buy > 90:
        #             if self.can_buy > 100:
        #                 self.to_buy = 100
        #             else:
        #                 self.to_buy = self.can_buy - 1
        #             val_check = "Value check " + self.pair + " " + "{:.8f}".format(self.price_to_buy) + " " + "{:.8f}".format(self.to_buy)
        #             print(val_check)
        #             placed_order = polo.buy(self.pair, "{:.8f}".format(self.price_to_buy), "{:.8f}".format(self.to_buy))
        #             print("Buy order placed!")
        #             print(placed_order)
        #
        #     if self.open_sell_flag == False and self.GRC_bal > 90:
        #         if self.GRC_bal > 100:
        #              self.to_sell = 100
        #         else:
        #             self.to_sell = self.GRC_bal - 1
        #         val_check = "Value check " + self.pair + " " + "{:.8f}".format(self.price_to_sell) + " " + "{:.8f}".format(self.to_sell)
        #         print(val_check)
        #         placed_order = polo.sell(self.pair, "{:.8f}".format(self.price_to_sell), "{:.8f}".format(self.to_sell))
        #         print("Sell order placed!")
        #         print(placed_order)


    # def Order_book(self, pair):
    #     self.orders = polo.returnOrderBook(pair, 5)
    #     self.high_bid_price = float(self.orders['bids'][0][0])
    #     self.high_bid_amount = float(self.orders['bids'][0][1])
    #     self.low_ask_price = float(self.orders['asks'][0][0])
    #     self.low_ask_amount = float(self.orders['asks'][0][1])


    def updateOpenTrades(self):
        print('BEFORE trade update the flags were:')
        print('Place orders flag = ' + str(self.place_orders_flag))
        print('Open buy flag = ' + str(self.open_buy_flag))
        print('Open sell flag = ' + str(self.open_sell_flag))

        self.openTrades = polo.returnOpenOrders(self.pair)
        self.open_Bids = []
        self.open_Asks = []

        if len(self.openTrades) == 0:
            self.open_buy_flag = False
            self.open_sell_flag = False
            print('Open trade flags set to False because openTrades was empty')

        elif len(self.openTrades) > 0:
            for trade in self.openTrades:
                order_Type = trade['type']
                order_Num = trade['orderNumber']
                if order_Type == 'buy':
                    self.open_Bids.append(order_Num)
                elif order_Type == 'sell':
                    self.open_Asks.append(order_Num)

        if len(self.open_Bids) == 0:
            self.open_buy_flag = False
            print('Open buy flag set to false because openTrades > 0 and no bids')
        if len(self.open_Asks) == 0:
            self.open_sell_flag = False
            print('Open sell flag set to false because openTrades > 0 and no asks')

        # Originally was outside the above if block
        # for trade in self.openTrades:
        #     order_Type = trade['type']
        #     order_Num = trade['orderNumber']
        #     if order_Type == 'buy':
        #         self.open_Bids.append(order_Num)
        #     elif order_Type == 'sell':
        #         self.open_Asks.append(order_Num)
        #
        # if len(self.open_Bids) == 0:
        #     self.open_buy_flag = False
        # if len(self.open_Asks) == 0:
        #     self.open_sell_flag = False

        if len(self.openTrades) > 0:
            print('openTrades was not empty so trades were checked')
            self.output.log(self.openTrades)

            if self.place_orders_flag == False:
                for trade in self.openTrades:
                    order_Num = trade['orderNumber']
                    polo.cancelOrder(order_Num)
                print('Spread too small, all orders cancelled')

            elif self.place_orders_flag == True:

                for trade in self.openTrades:
                    order_Num = trade['orderNumber']
                    order_Type = trade['type']
                    order_price = float(trade['rate'])
                    if order_Type == "buy":
                        if order_price == self.price_to_buy:
                            self.open_buy_flag = True
                            print("Previous buy order still open at target price")
                            print('Open buy flag set to True because previous order exists')
                        elif order_price != self.price_to_buy:
                            polo.cancelOrder(order_Num)
                            print("Buy order closed")
                            self.open_buy_flag = False
                            print('Open buy flag set to False due to cancelled trade')
                    elif order_Type == "sell":
                        if order_price == self.price_to_sell:
                            self.open_sell_flag = True
                            print("Previous sell order still open at target price.")
                            print('Open sell flag set to True because previous order exists')
                        elif order_price != self.price_to_sell:
                            polo.cancelOrder(order_Num)
                            print("Sell order closed")
                            self.open_sell_flag = False
                            print('Open sell flag set to False due to cancelled trade')
            self.openTrades = polo.returnOpenOrders(self.pair)

        print('AFTER trade update the flags were:')
        print('Place orders flag = ' + str(self.place_orders_flag))
        print('Open buy flag = ' + str(self.open_buy_flag))
        print('Open sell flag = ' + str(self.open_sell_flag))


    def set_order_prices(self):
        self.balance = polo.returnBalances()
        self.GRC_bal = float(self.balance['GRC'])
        self.BTC_bal = float(self.balance['BTC'])
        self.Total_bal = self.GRC_bal + (self.BTC_bal / float(self.currentPrice))

        self.orders = polo.returnOrderBook(self.pair, 5)
        self.high_bid_price = float(self.orders['bids'][0][0])
        self.high_bid_amount = float(self.orders['bids'][0][1])
        self.low_ask_price = float(self.orders['asks'][0][0])
        self.low_ask_amount = float(self.orders['asks'][0][1])
        self.output.log("High bid: " + str(self.high_bid_price) + " Low ask: " + str(self.low_ask_price))

        self.raw_spread = self.low_ask_price - self.high_bid_price
        print('Raw spread = ' + str(self.raw_spread))

        if self.raw_spread >= 7E-8:
            if self.high_bid_amount > 100:
                self.price_to_buy = self.high_bid_price + 1E-8
            else:
                self.price_to_buy = self.high_bid_price

            if self.low_ask_amount > 100:
                self.price_to_sell = self.low_ask_price - 1E-8
            else:
                self.price_to_sell = self.low_ask_price

            self.place_orders_flag = True

        elif self.raw_spread < 7E-8:
            orders = self.orders

            bids = []

            for x in orders['bids']:
                bid_price = x[0]
                bid_amount = x[1]
                bids.append([bid_price, bid_amount])

            bids_running_sum = 0
            bids_index_counter = 0

            for y in bids:
                bids_running_sum += float(y[1])
                if bids_running_sum > 1000 and bids_index_counter == 0:
                    buy_price_index = 0
                    overcut = True
                    break
                elif bids_running_sum > 1000 and bids_index_counter > 0:
                    buy_price_index = bids_index_counter - 1
                    overcut = False
                    break
                else:
                    buy_price_index = bids_index_counter
                    overcut = False
                bids_index_counter += 1

            if overcut == True:
                self.price_to_buy = self.high_bid_price + 1E-8
                print('Overcutting')
            else:
                print('Buy at index: ' + str(buy_price_index))
                price_to_buy_txt = str(bids[buy_price_index][0])
                self.price_to_buy = float(price_to_buy_txt)

            asks = []

            for x in orders['asks']:
                ask_price = x[0]
                ask_amount = x[1]
                asks.append([ask_price, ask_amount])

            asks_running_sum = 0
            asks_index_counter = 0

            for y in asks:
                asks_running_sum += float(y[1])
                if asks_running_sum > 1000 and asks_index_counter == 0:
                    sell_price_index = 0
                    undercut = True
                    break
                elif asks_running_sum > 1000 and asks_index_counter > 0:
                    sell_price_index = asks_index_counter - 1
                    undercut = False
                    break
                else:
                    sell_price_index = asks_index_counter
                    undercut = False
                asks_index_counter += 1

            if undercut == True:
                self.price_to_sell = self.low_ask_price - 1E-8
                print('Undercutting')
            else:
                price_to_sell_txt = str(asks[sell_price_index][0])
                self.price_to_sell = float(price_to_sell_txt)

            print('Sell price = ' + str(self.price_to_sell))
            print('Buy price = ' + str(self.price_to_buy))
            self.mod_spread = self.price_to_sell - self.price_to_buy
            print('Modified spread = ' + str(self.mod_spread))

            if self.mod_spread <= 1.01E-8:
                self.place_orders_flag = False
                print('Set place orders flag to False because spread too small')
            elif self.price_to_sell <= self.high_bid_price:
                self.place_orders_flag = False
                print('Set place orders flag to false due to avoid cross-selling')
            elif self.price_to_buy >= self.low_ask_price:
                self.place_orders_flag = False
                print('Set place orders flag to false due to avoid cross-buying')
            else:
                self.place_orders_flag = True
                print('Set place orders flag to True, all conditions met')

            print('Place orders flag = ' + str(self.place_orders_flag))
