
import math
import numpy as np
import pandas as pd
import dateutil
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()


class CdoAnalyzer:
    def __init__(self,
                 default_dates=[],
                 bond_size=10,
                 default_probability=0.04,
                 lgd=0.6,
                 face_value=10000000,
                 coupon_rate=0.06,
                 years=5,
                 frequency=4,
                 risk_free_rate=0.01,
                 notional_A=20000000,
                 notional_B=10000000,
                 coupon_rate_A=0.02,
                 coupon_rate_B=0.04,
                 discount_rate_bond=0.09,
                 discount_rate_A=0.015,
                 discount_rate_B=0.05):

        self.default_dates = default_dates
        self.bond_size = bond_size
        self.default_probability = default_probability
        self.lgd = lgd
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.years = years
        self.frequency = frequency
        self.risk_free_rate = risk_free_rate
        self.notional_A = notional_A
        self.notional_B = notional_B
        self.coupon_rate_A = coupon_rate_A
        self.coupon_rate_B = coupon_rate_B
        self.discount_rate_bond = discount_rate_bond
        self.discount_rate_A = discount_rate_A
        self.discount_rate_B = discount_rate_B

        self.portfolio_value = np.nan
        self.periods = self.years * self.frequency
        self.sim_size = len(default_dates)

        self.sim_cashflow = []
        self.sim_result = pd.DataFrame(index=range(self.sim_size),
                                       columns=['classA_default', 'classB_default', 'classA_lgd', 'classB_lgd',
                                                'classA_value', 'classB_value', 'equity_value', 'equity_IRR'])
        self.sim_statistics = {'classA_default_rate': np.nan,
                               'classB_default_rate': np.nan,
                               'classA_lgd': np.nan,
                               'classB_lgd': np.nan,
                               'classA_value': np.nan,
                               'classB_value': np.nan,
                               'equity_value': np.nan,
                               'equity_ROE': np.nan}
        # self._initialize_cashflow()
        self._get_discount_factor()
        self._get_portfolio_value()

        self.notional_equity = self.portfolio_value - self.notional_A - self.notional_B

    def _initialize_cashflow(self):
        bond_cashflow_values = np.ones((self.periods, self.bond_size)) * self.face_value * self.coupon_rate / self.frequency
        bond_cashflow_values[-1, :] += self.face_value
        other_cashflow_values = np.zeros((self.periods, 6))
        self.sim_cashflow = [pd.DataFrame(np.hstack((bond_cashflow_values, other_cashflow_values)),
                                          index=list(range(1, self.periods + 1)),
                                          columns=['bond_' + str(i) for i in range(self.bond_size)] +
                                                  ['aggregated_cf', 'classA_required', 'classA_get', 'classB_required',
                                                   'classB_get', 'equity_get'])
                             ] * self.sim_size

    def _get_discount_factor(self):
        self.discount_factor_bond = (
                    (1 / (1 + self.discount_rate_bond / self.frequency)) * np.ones((self.periods))).cumprod()
        self.discount_factor_A = ((1 / (1 + self.discount_rate_A / self.frequency)) * np.ones((self.periods))).cumprod()
        self.discount_factor_B = ((1 / (1 + self.discount_rate_B / self.frequency)) * np.ones((self.periods))).cumprod()

    def _get_portfolio_value(self):
        payment = self.face_value * self.coupon_rate / self.frequency
        self.portfolio_value = self.bond_size * (payment / (self.discount_rate_bond / self.frequency) * (1 - 1/(1 + self.discount_rate_bond / self.frequency)**self.periods)
                                                 + self.face_value/(1+self.discount_rate_bond/self.frequency)**self.periods)

    def get_default_rate_parameters(self, notionals_A):
        origin_notional_A = self.notional_A
        default_rates_A = []
        for notional in notionals_A:
            self._update_notional_A(notional)
            self.run()
            default_rates_A.append(self.sim_statistics['classA_default_rate'])
        multi_default_rate = pd.DataFrame({'classA_notional': notionals_A,
                                           'classA_default_rate': default_rates_A})

        self._update_notional_A(origin_notional_A)
        self.run()
        return multi_default_rate

    def _update_notional_A(self, notional_A):
        self.notional_A = notional_A
        self.notional_equity = self.portfolio_value - self.notional_A - self.notional_B

    def _update_notional_B(self, notional_B):
        self.notional_B = notional_B
        self.notional_equity = self.portfolio_value - self.notional_A - self.notional_B

    def run(self):
        self._initialize_cashflow()
        self._get_bond_cf()
        self._get_portfolio_cf()
        self._get_class_required_cf()
        self._get_class_get_cf()
        self._get_sim_result()
        self._get_sim_statistics()

    def _get_bond_cf(self):
        for sim_num in range(self.sim_size):
            self.sim_cashflow[sim_num] = self.sim_cashflow[sim_num].fillna(self.face_value * self.coupon_rate / self.frequency)

            for bond_num in range(self.bond_size):
                bond_name = 'bond_' + str(bond_num)
                default_period = math.ceil(self.default_dates[sim_num][bond_num])
                if default_period < self.periods:
                    self.sim_cashflow[sim_num][bond_name].loc[default_period:] = self.sim_cashflow[sim_num][bond_name].loc[default_period:] * (1 - self.lgd)
            self.sim_cashflow[sim_num] = self.sim_cashflow[sim_num].fillna(0)

    def _get_portfolio_cf(self):
        for sim_num in range(self.sim_size):
            self.sim_cashflow[sim_num]['aggregated_cf'] = self.sim_cashflow[sim_num][
                                                        ['bond_' + str(i) for i in range(self.bond_size)]].sum(axis=1)

    def _get_class_required_cf(self):
        for sim_num in range(self.sim_size):
            self.sim_cashflow[sim_num]['classA_required'] = self.notional_A * self.coupon_rate_A \
                                                            / self.frequency
            self.sim_cashflow[sim_num]['classA_required'].iloc[-1] += self.notional_A
            self.sim_cashflow[sim_num]['classB_required'] = self.notional_B * self.coupon_rate_B \
                                                            / self.frequency
            self.sim_cashflow[sim_num]['classB_required'].iloc[-1] += self.notional_B

    def _get_class_get_cf(self):
        for sim_num in range(self.sim_size):
            self.sim_cashflow[sim_num]['classA_get'] = self.sim_cashflow[sim_num][['aggregated_cf', 'classA_required']].min(axis=1)
            self.sim_cashflow[sim_num]['cf_afterA'] = self.sim_cashflow[sim_num]['aggregated_cf'] - self.sim_cashflow[sim_num]['classA_get']
            self.sim_cashflow[sim_num]['classB_get'] = self.sim_cashflow[sim_num][['cf_afterA', 'classB_required']].min(axis=1)
            self.sim_cashflow[sim_num]['equity_get'] = self.sim_cashflow[sim_num]['aggregated_cf'] \
                                                       - self.sim_cashflow[sim_num]['classA_get'] \
                                                       - self.sim_cashflow[sim_num]['classB_get']

    def _get_sim_result(self):
        for sim_num in range(self.sim_size):
            self.sim_result.loc[sim_num]['classA_default'] = sum(abs(self.sim_cashflow[sim_num]['classA_required']
                                                                     - self.sim_cashflow[sim_num]['classA_get'])) != 0
            self.sim_result.loc[sim_num]['classB_default'] = sum(abs(self.sim_cashflow[sim_num]['classB_required']
                                                                     - self.sim_cashflow[sim_num]['classB_get'])) != 0
            self.sim_result.loc[sim_num]['classA_lgd'] = 1 - self.sim_cashflow[sim_num]['classA_get'].sum()\
                                                            / self.sim_cashflow[sim_num]['classA_required'].sum()
            self.sim_result.loc[sim_num]['classB_lgd'] = 1 - self.sim_cashflow[sim_num]['classB_get'].sum() \
                                                            / self.sim_cashflow[sim_num]['classB_required'].sum()
            self.sim_result.loc[sim_num]['classA_value'] = (self.sim_cashflow[sim_num]['classA_get']
                                                            * self.discount_factor_A).sum()
            self.sim_result.loc[sim_num]['classB_value'] = (self.sim_cashflow[sim_num]['classB_get']
                                                          * self.discount_factor_B).sum()
            self.sim_result.loc[sim_num]['equity_value'] = self.portfolio_value \
                                                           - self.sim_result.loc[sim_num]['classA_value'] \
                                                           - self.sim_result.loc[sim_num]['classB_value']

            self.sim_result.loc[sim_num]['equity_IRR'] = np.irr(
                np.hstack((-np.ones((1,)) * self.sim_result.loc[sim_num]['equity_value'],
                           self.sim_cashflow[sim_num]['equity_get'].values))
            ) * self.frequency


    def _get_sim_statistics(self):
        self.sim_statistics['classA_default_rate'] = self.sim_result['classA_default'].mean() / self.years
        self.sim_statistics['classB_default_rate'] = self.sim_result['classB_default'].mean() / self.years
        self.sim_statistics['classA_lgd'] = self.sim_result[self.sim_result['classA_default']]['classA_lgd'].mean()
        self.sim_statistics['classB_lgd'] = self.sim_result[self.sim_result['classB_default']]['classB_lgd'].mean()
        self.sim_statistics['classA_value'] = self.sim_result['classA_value'].mean()
        self.sim_statistics['classB_value'] = self.sim_result['classB_value'].mean()
        self.sim_statistics['equity_value'] = self.sim_result['equity_value'].mean()
        self.sim_statistics['equity_ROE'] = self.sim_result['equity_IRR'].mean()


if __name__ == '__main__':

    analyzer = CdoAnalyzer(
        default_dates=[[1.5, 1.2, 3.1, 1, 1],
                       [7, 7.3, 8.7, 17, 20],
                       [1.1, 1.9, 2.3, 5, 6],
                       [8, 1, 9, 9, 10.2],
                       [7.1, 5.2, 6.6, 8.8, 9.9]],
        bond_size=5,
        default_probability=0.04,
        lgd=0.6,
        face_value=10000000,
        coupon_rate=0.06,
        years=5,
        frequency=4,
        risk_free_rate=0.01,
        notional_A=20000000,
        notional_B=10000000,
        coupon_rate_A=0.02,
        coupon_rate_B=0.04,
        discount_rate_bond=0.09,
        discount_rate_A=0.015,
        discount_rate_B=0.05
    )
    analyzer.run()
    # multi_default_rate = analyzer.get_default_rate_parameters(notionals_A=list(range(10000000, 80000000, 5000000)))
    sim_cashflow = analyzer.sim_cashflow[0]
    sim_result = analyzer.sim_result
    sim_stat = analyzer.sim_statistics
    print(sim_stat)