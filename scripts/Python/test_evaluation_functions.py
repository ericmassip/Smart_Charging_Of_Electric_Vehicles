import unittest
import numpy as np
import pandas as pd

from evaluation_function import get_optimal_cost, get_BAU_cost
from session_helper import charging_rate


class StateActionTuples(unittest.TestCase):

    def setUp(self):
        sessions = pd.read_csv('~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-03-06.csv')
        # sessions_of_the_day = [sessions.loc[1], sessions.loc[2], sessions.loc[3]]
        self.sessions_of_the_day = [sessions.loc[15], sessions.loc[16]]

    def tearDown(self):
        sessions_of_the_day = []
        testing_days = []

    def test_BAU_cost(self):
        actual_optimal_cost = get_BAU_cost(self.sessions_of_the_day)
        expected_optimal_cost = (1 * 1 * charging_rate) * 3

        self.assertEqual(expected_optimal_cost, actual_optimal_cost)


if __name__ == '__main__':
    unittest.main()
