from numpy import sign

# The core codes are from the following path
# https://github.com/quantstart/qstrader/tree/master/qstrader
# Still need time to develop codes for a real broker

class Position(object):
    def __init__(self, action, ticker, quantity, price, commission, bid, ask):
        self.action     = action
        self.ticker     = ticker
        self.quantity   = quantity
        self.init_price = price
        self.init_commission = commission

        self.realised_pnl = 0
        self.unrealised_pnl = 0

        self.buys = 0
        self.sells = 0
        self.avg_bot = 0
        self.avg_sld = 0
        self.total_bot = 0
        self.total_sld = 0
        self.total_commission = commission

        self.__setup__()

        self.update(bid, ask)
        
    def __setup__(self):
        if self.action == "BOT":
            self.buys       = self.quantity
            self.avg_bot    = self.init_price
            self.total_bot  = self.buys * self.avg_bot
            self.avg_price  = (self.init_price * self.quantity + self.init_commission) // self.quantity
            self.cost_basis = self.quantity * self.avg_price
        else:  # action == "SLD"
            self.sells      = self.quantity
            self.avg_sld    = self.init_price
            self.total_sld  = self.sells * self.avg_sld
            self.avg_price  = (self.init_price * self.quantity - self.init_commission) // self.quantity
            self.cost_basis = -self.quantity * self.avg_price

        self.net = self.buys - self.sells
        self.net_total = self.total_sld - self.total_bot
        self.net_incl_comm = self.net_total - self.init_commission

    def update(self, bid, ask):
        """
        The market value is tricky to calculate as we only have
        access to the top of the order book through Interactive
        Brokers, which means that the true redemption price is
        unknown until executed.
        However, it can be estimated via the mid-price of the
        bid-ask spread. Once the market value is calculated it
        allows calculation of the unrealised and realised profit
        and loss of any transactions.
        """
        midpoint = (bid + ask) // 2
        self.market_value = self.quantity * midpoint * sign(self.net)
        self.unrealised_pnl = self.market_value - self.cost_basis

    def transact(self, action, quantity, price, commission):
        """
        Calculates the adjustments to the Position that occur
        once new shares are bought and sold.
        Takes care to update the average bought/sold, total
        bought/sold, the cost basis and PnL calculations,
        as carried out through Interactive Brokers TWS.
        """
        self.total_commission += commission

        # Adjust total bought and sold
        if action == "BOT":
            self.avg_bot = (
                self.avg_bot * self.buys + price * quantity
            ) // (self.buys + quantity)
            if self.action != "SLD":  # Increasing long position
                self.avg_price = (
                    self.avg_price * self.buys +
                    price * quantity + commission
                ) // (self.buys + quantity)
            elif self.action == "SLD":  # Closed partial positions out
                self.realised_pnl += quantity * (
                    self.avg_price - price
                ) - commission  # Adjust realised PNL
            self.buys += quantity
            self.total_bot = self.buys * self.avg_bot

        # action == "SLD"
        else:
            self.avg_sld = (
                self.avg_sld * self.sells + price * quantity
            ) // (self.sells + quantity)
            if self.action != "BOT":  # Increasing short position
                self.avg_price = (
                    self.avg_price * self.sells +
                    price * quantity - commission
                ) // (self.sells + quantity)
                self.unrealised_pnl -= commission
            elif self.action == "BOT":  # Closed partial positions out
                self.realised_pnl += quantity * (
                    price - self.avg_price
                ) - commission
            self.sells += quantity
            self.total_sld = self.sells * self.avg_sld

        # Adjust net values, including commissions
        self.net = self.buys - self.sells
        self.quantity = self.net
        self.net_total = self.total_sld - self.total_bot
        self.net_incl_comm = self.net_total - self.total_commission

        # Adjust average price and cost basis
        self.cost_basis = self.quantity * self.avg_price

    def net_count(self):
        return self.quantity;
        
class Portfolio:
    ACTION_BUY  = "BOT"
    ACTION_SELL = "SLD"

    def __init__(self, price_quoter, start_cash, log_handler):
        self.price_quoter = price_quoter
        self.init_cash    = start_cash
        self.all_equity   = start_cash
        self.cur_cash     = start_cash
        self.positions    = {}
        self.closed_positions = []
        self.realised_pnl = 0
        self.log_handler  = log_handler
        
    def __update__(self):
        self.unrealised_pnl = 0
        self.all_equity = self.realised_pnl
        self.all_equity += self.init_cash

        for ticker in self.positions:
            position = self.positions[ticker]
            if self.price_quoter.is_tick():
                bid, ask = self.price_quoter.best_bid_ask(ticker)
            else:
                close_price = self.price_quoter.close(ticker)
                bid = close_price
                ask = close_price

            position.update(bid, ask)

            self.unrealised_pnl += position.unrealised_pnl
            self.all_equity += (
                position.market_value - position.cost_basis + position.realised_pnl
            )

    def __add__(self, action, ticker, quantity, price, commission):
        if ticker not in self.positions:
            if self.price_quoter.is_tick():
                bid, ask = self.price_quoter.best_bid_ask(ticker)
            else:
                close_price = self.price_quoter.close(ticker)
                bid = close_price
                ask = close_price

            position = Position(action, ticker, quantity, price, commission, bid, ask)
            self.positions[ticker] = position
            self.__update__()
        else:
            self.log_handler.error(
                "Ticker %s is already in the positions list. "
                "Could not add a new position." % ticker
            )

    def __modify__(self, action, ticker, quantity, price, commission):
        if ticker in self.positions:
            self.positions[ticker].transact(
                action, quantity, price, commission
            )
            if self.price_quoter.is_tick():
                bid, ask = self.price_quoter.get_best_bid_ask(ticker)
            else:
                close_price = self.price_quoter.close(ticker)
                bid = close_price
                ask = close_price

            self.positions[ticker].update(bid, ask)
            if self.positions[ticker].quantity == 0:
                closed = self.positions.pop(ticker)
                self.realised_pnl += closed.realised_pnl
                self.closed_positions.append(closed)

            self.__update__()
        else:
            self.log_handler.error(
                "Ticker %s not in the current position list. "
                "Could not modify a current position." % ticker
            )

    def transact(self, action, ticker_id, quantity, price, commission):
        if action == Portfolio.ACTION_BUY:
            self.cur_cash -= ((quantity * price) + commission)
        elif action == Portfolio.ACTION_SELL:
            self.cur_cash += ((quantity * price) - commission)

        if ticker_id not in self.positions:
            self.__add__(action, ticker_id, quantity, price, commission)
        else:
            self.__modify__(action, ticker_id, quantity, price, commission)

    def quantity(self, ticker_id):
        position = self.positions.get(ticker_id, None)
        if position is None:
            return 0
        else:
            return position.net_count()
    
    def update(self):
        self.__update__()

    def cash(self):
        return self.cur_cash
        
    def equity(self):
        return self.all_equity