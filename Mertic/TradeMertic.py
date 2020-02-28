class TradeMertic:
    def __init__(self, benchmark, periods, log_handler):
        self.benchmark    = benchmark
        self.periods      = periods
        self.trade_info   = {}
        self.trade_mertic = {}
        self.log_handler  = log_handler
        
    def record(self, time_stamp, equity_all, buy_price, sell_price):
        self.trade_info['time_stamp'] = time_stamp
        self.trade_info['equity_all'] = equity_all
        self.trade_info['buy_price']  = buy_price
        self.trade_info['sell_price'] = sell_price
        
    def update(self):
        equity_s = pd.Series(self.equity).sort_index()
        returns_s = equity_s.pct_change().fillna(0.0)
        rolling = returns_s.rolling(window = self.periods)
        rolling_sharpe_s = np.sqrt(self.periods) * (
            rolling.mean() / rolling.std()
        )

        # Cummulative Returns
        cum_returns_s = np.exp(np.log(1 + returns_s).cumsum())

        # Drawdown, max drawdown, max drawdown duration
        dd_s, max_dd, dd_dur = perf.create_drawdowns(cum_returns_s)


        # Equity statistics
        statistics["sharpe"] = perf.create_sharpe_ratio(
            returns_s, self.periods
        )

        statistics["drawdowns"] = dd_s
        # TODO: need to have max_drawdown so it can be printed at end of test
        trade_mertic["max_drawdown"] = max_dd
        trade_mertic["max_drawdown_pct"] = max_dd
        trade_mertic["max_drawdown_duration"] = dd_dur
        trade_mertic["equity"] = equity_s
        trade_mertic["returns"] = returns_s
        trade_mertic["rolling_sharpe"] = rolling_sharpe_s
        trade_mertic["cum_returns"] = cum_returns_s

        if self.benchmark is not None:
            equity_b = pd.Series(self.equity_benchmark).sort_index()
            returns_b = equity_b.pct_change().fillna(0.0)
            rolling_b = returns_b.rolling(window=self.periods)
            rolling_sharpe_b = np.sqrt(self.periods) * (
                rolling_b.mean() / rolling_b.std()
            )
            cum_returns_b = np.exp(np.log(1 + returns_b).cumsum())
            dd_b, max_dd_b, dd_dur_b = perf.create_drawdowns(cum_returns_b)
            statistics["sharpe_b"] = perf.create_sharpe_ratio(returns_b)
            statistics["drawdowns_b"] = dd_b
            statistics["max_drawdown_pct_b"] = max_dd_b
            statistics["max_drawdown_duration_b"] = dd_dur_b
            statistics["equity_b"] = equity_b
            statistics["returns_b"] = returns_b
            statistics["rolling_sharpe_b"] = rolling_sharpe_b
            statistics["cum_returns_b"] = cum_returns_b
