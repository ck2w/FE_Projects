
import numpy as np
import pandas as pd
np.random.seed(0)

from DefaultDateSimulator import DefaultDateSimulator
from CdoAnalyzer import CdoAnalyzer

simulator = DefaultDateSimulator(
    sim_size=10000,
    bond_size=10,
    frequency=4,
    default_probability=0.04,
    target_correlation=0.2)

simulator.run()

sim_default_dates = simulator.correlated_poisson

analyzer = CdoAnalyzer(
    default_dates=sim_default_dates,
    bond_size=10,
    default_probability=0.04,
    lgd=0.6,
    face_value=10,
    coupon_rate=0.06,
    years=5,
    frequency=4,
    risk_free_rate=0.01,
    notional_A=52.5,
    notional_B=10,
    coupon_rate_A=0.02,
    coupon_rate_B=0.04,
    discount_rate_bond=0.09,
    discount_rate_A=0.015,
    discount_rate_B=0.05  # hw: 0.05, class:0.03
)
analyzer.run()
# multi_default_rate = analyzer.get_default_rate_parameters(notionals_A=list(range(30000000, 90000000, 10000000)))
sim_cashflow = analyzer.sim_cashflow[4]
sim_result = analyzer.sim_result
sim_stat = analyzer.sim_statistics
print(pd.Series(sim_stat))


# notionalA, sim_size=1000, years=5
# 49: DP=0.02%, IRR=14.99%
# 51: DP=0.02%, IRR=15.99%
# 52: DP=0.02%, IRR=16.54%
# 52.5: DP=0.02%, IRR=16.83%
# 53: DP=0.1%, IRR=17.14%
# 55: DP=0.1%, IRR=18.48%

# notionalA, sim_size=10000, years=5
# 52.5: DP=0.018%, IRR=16.99%
# 52.7: DP=0.088%, IRR=17.1074%
# 53: DP=0.088%, IRR=17.29%
# 54: DP=0.08%, IRR=17.93%
