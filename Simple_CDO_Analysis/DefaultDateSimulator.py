
import numpy as np
from scipy.stats import norm
np.set_printoptions(precision=3, suppress=True)
np.random.seed(0)


class DefaultDateSimulator:
    def __init__(self,
                 sim_size=1000,
                 bond_size=10,
                 frequency=4,
                 default_probability=0.04,
                 target_correlation=0.2):

        self.sim_size = sim_size
        self.bond_size = bond_size
        self.frequency = frequency
        self.default_probability = default_probability
        self.target_correlation = target_correlation

        self.target_correlation_matrix = self._build_correlation_matrix()
        self.target_correlation_matrix_cholesky = self._cholesky_decomposition(self.target_correlation_matrix)

        self.clean_normals = None
        self.correlated_geometric = None

    def _build_correlation_matrix(self):
        mat = np.ones((self.bond_size, self.bond_size)) * self.target_correlation
        for i in range(self.bond_size):
            mat[i, i] = 1
        return mat

    def run(self):
        self._get_clean_normals()
        self._get_correlated_possion()

    def _get_clean_normals(self):
        dirty_normals = np.random.normal(0, 1, size=(self.sim_size, self.bond_size))
        # demean
        demean_normals = dirty_normals - dirty_normals.mean(axis=0)
        # moment matching
        cov_normals = np.cov(demean_normals.T)
        cov_normals_cholesky = self._cholesky_decomposition(cov_normals)
        self.clean_normals = np.dot(demean_normals, self._inverse_matrix(cov_normals_cholesky.T))
        self._sanity_check_matrix(self.clean_normals, 'Normals after Moment Matching')

    def _get_correlated_possion(self):
        correlated_normals = np.dot(self.clean_normals, self.target_correlation_matrix_cholesky.T)
        self._sanity_check_matrix(correlated_normals, 'Correlated Normals')
        correlated_uniform = norm.cdf(correlated_normals)
        self.correlated_poisson = -np.log(1 - correlated_uniform) / (self.default_probability / self.frequency)

    def _sanity_check_matrix(self, matrix, text='sanity check'):
        print('----------------------------')
        print(text)
        print('----------------------------')
        print('Matrix Mean:')
        print(matrix.mean(axis=0))
        print('Matrix Covariance:')
        print(np.cov(matrix.T))

    def _inverse_matrix(self, matrix):
        return np.linalg.inv(matrix)

    def _cholesky_decomposition(self, matrix):
        return np.linalg.cholesky(matrix)

if __name__ == '__main__':
    simulator = DefaultDateSimulator(
        sim_size=1000,
        bond_size=10,
        frequency=4,
        default_probability=0.04,
        target_correlation=0.2)

    simulator.run()
    default_dates = simulator.correlated_geometric