# RSI Formula
#                          100
# rsi = 100 - -----------------------------
#             1 + Average gain/Average loss

class RsiStrategy:
    __some_large_number = 9999999999

    @staticmethod
    def rolling_average(prices: list, length: int) -> list:
        cumsum, moving_aves = [0], []

        for i, x in enumerate(prices, 1):
            cumsum.append(cumsum[i - 1] + x)
            if i >= length:
                moving_ave = (cumsum[i] - cumsum[i - length]) / length
                # can do stuff with moving_ave here
                moving_aves.append(moving_ave)
        return moving_aves

    @staticmethod
    def calc_rsi(price: list, length: int) -> list:
        delta = [y - x for x, y in zip(price[:len(price) - 1], price[1:])]

        # 1   1       Z   1   2   ->  +1
        # 2   2   2   I   2   3   ->  +1
        # 3       3   P

        dUp, dDown = delta.copy(), delta.copy()

        # create list of up and down moves for the past periods. Fill with zeros where necessary
        dUp = [x if x > 0 else 0 for x in dUp]
        dDown = [x if x < 0 else 0 for x in dDown]

        # Create rolling averages for each of the up and down moves followed by an inversion of the negative rolling avg
        RolUp = RsiStrategy.rolling_average(dUp, length)
        RolDown = [abs(x) for x in RsiStrategy.rolling_average(dDown, length)]

        # calculate a list for a time series: RS = Average Gain / Average Loss
        RS = [avg_gain / avg_loss if avg_loss != 0 else RsiStrategy.__some_large_number for avg_gain, avg_loss in
              zip(RolUp, RolDown)]

        # calculate the RSI based on the formula
        return [0] * length + [100.0 - (100.0 / (1.0 + x)) for x in RS]

    @staticmethod
    def calc_trades(timestamp, prices, rsi):

        # output trade list
        pre_trades = []

        # prelimenary variables
        stoploss = 0.1
        activeTrade = False
        currentTrade = []

        for t, price, rsi_val in zip(timestamp, prices, rsi):

            if not activeTrade:
                if rsi_val > 70:
                    currentTrade = [t, price, 'short']
                    activeTrade = True
                if rsi_val < 30:
                    currentTrade = [t, price, 'long']
                    activeTrade = True

            if activeTrade:
                entry_price = currentTrade[1]
                pos_direction = currentTrade[2]

                # stoploss trigger on long position
                if pos_direction == 'long' and price < entry_price * (1 - stoploss):
                    pre_trades.append(currentTrade + [price])
                    activeTrade = False

                # stoploss trigger on short position
                if pos_direction == 'short' and price > entry_price * (1 + stoploss):
                    pre_trades.append(currentTrade + [price])
                    activeTrade = False

                # take profit trigger on long position
                if pos_direction == 'long' and rsi_val > 70:
                    pre_trades.append(currentTrade + [price])

                    # open short position as RSI is above 70
                    currentTrade = [t, price, 'short']

                # take profit trigger on short position
                if pos_direction == 'short' and rsi_val < 30:
                    pre_trades.append(currentTrade + [price])

                    # open long position as RSI is below 30
                    currentTrade = [t, price, 'long']

        return pre_trades


# ticker_data = [100, 102, 103, 108, 105, 107, 200, 197, 198, 205, 199, 206, 205, 210, 205, 209, 211, 208, 400]
# price_with_rsi = RsiStrategy.calc_rsi(ticker_data, 14)[14:]
#
# print(RsiStrategy.calc_trades(range(0, len(ticker_data[14:])), ticker_data[14:], price_with_rsi))
