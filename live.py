import sys, getopt
import time
import urllib2

from botchart import BotChart
from strat_Market_Make_live import BotStrategy
# from strat_market_make_Fold import BotStrategy_FLDC
from botlog import BotLog
from botcandlestick import BotCandlestick

def main(argv):
    chart = BotChart("poloniex", "BTC_GRC", 60, False)  # the period is for back testing, so actually obsolete

    strategy = BotStrategy()
    # strategy_FLDC = BotStrategy_FLDC()

    candlesticks = []
    developingCandlestick = BotCandlestick(period = 60)

    while True:
        try:
            developingCandlestick.tick(chart.getCurrentPrice())
        except urllib2.URLError:
            time.sleep(int(30))
            developingCandlestick.tick(chart.getCurrentPrice())

        if developingCandlestick.isClosed():
            candlesticks.append(developingCandlestick)
            strategy.tick(developingCandlestick)
            # strategy_FLDC.tick()
            developingCandlestick = BotCandlestick(period = 60)

        # strategy.evaluatePositions_raw_gap()
        time.sleep(int(30))

if __name__ == "__main__":
    main(sys.argv[1:])
