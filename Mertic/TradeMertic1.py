def TradeMertic:
    def __init__(self, period, log_handler):
        self.trade_info    = pandas.DataFrame()
        self.mertic_list   = []
        self.mertic_period = period
        self.log_handler   = log_handler

    def record(self, time_stamp, equity_all):        
        record = { 'time_stamp': time_stamp,
                   'equity_all': equity_all }

        self.trade_info = self.trade_info.append(
            record, ignore_index = True
        )

    def append(self, metric_list):
        if 'Shapre' in mertic_list:
            self.mertic_list.append(SharpeRatio())
        if 'DropDown' in mertic_list:
            self.mertic_list.append(DropDown())

    def mertic(self):
        equity_s = pd.Series(self.equity).sort_index()
        returns_s = equity_s.pct_change().fillna(0.0)

        for mertic in self.mertic_list:
            mertic(returns, self.period)
        
class SharpeRatio:
    def __init(self):
        pass

    def mertic(returns, period = 252):
        return np.sqrt(period) * (np.mean(returns)) / np.std(returns)

class DropDown:
    def __init__(self):
        pass

    def mertic():
        # Calculate the cumulative returns curve
        # and set up the High Water Mark
        idx = returns.index
        hwm = np.zeros(len(idx))

        # Create the high water mark
        for t in range(1, len(idx)):
            hwm[t] = max(hwm[t - 1], returns.ix[t])

        # Calculate the drawdown and duration statistics
        perf = pd.DataFrame(index=idx)
        perf["Drawdown"] = (hwm - returns) / hwm
        perf["Drawdown"].ix[0] = 0.0
        perf["DurationCheck"] = np.where(perf["Drawdown"] == 0, 0, 1)
        duration = max(
            sum(1 for i in g if i == 1)
            for k, g in groupby(perf["DurationCheck"])
        )

        return perf["Drawdown"], np.max(perf["Drawdown"]), duration
