from collections import deque
class MetricsBuffer:
    def __init__(self, maxlen=100):
        self.timestamps = deque(maxlen=maxlen)
        self.slippages = deque(maxlen=maxlen)
        self.impacts = deque(maxlen=maxlen)
        self.fees = deque(maxlen=maxlen)
        self.net_costs = deque(maxlen=maxlen)
        self.latencies = deque(maxlen=maxlen)
        self.maker_taker_roles = deque(maxlen=maxlen)

    def add(self, timestamp, slippage, impact, fee, net_cost, latency, maker_taker_role):
        self.timestamps.append(timestamp)
        self.slippages.append(slippage)
        self.impacts.append(impact)
        self.fees.append(fee)
        self.net_costs.append(net_cost)
        self.latencies.append(latency)
        self.maker_taker_roles.append(maker_taker_role)
