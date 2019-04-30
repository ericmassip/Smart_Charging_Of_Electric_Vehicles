import unittest
import numpy as np
import pandas as pd

from evaluation_function import get_optimal_cost, get_BAU_cost
from session_helper import charging_rate

# For testing with Smax = 3, start_hour = 6 and end_hour = 12

class StateActionTuples(unittest.TestCase):

    def setUp(self):
        sessions = pd.read_csv('~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-03-06.csv')
        # sessions_of_the_day = [sessions.loc[1], sessions.loc[2], sessions.loc[3]]
        self.sessions_of_the_day = [sessions.loc[15], sessions.loc[16]]
        self.test_day_trajectories = ['/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/trajectories_2018-08-18.json', '/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/trajectories_2018-08-24.json']

    def tearDown(self):
        sessions_of_the_day = []

    def test_BAU_cost(self):
        actual_BAU_cost = get_BAU_cost(pd.DataFrame(self.sessions_of_the_day))
        expected_BAU_cost = (2 * 1 * charging_rate) + (2 * 1 * charging_rate)

        self.assertEqual(expected_BAU_cost, actual_BAU_cost)


if __name__ == '__main__':
    unittest.main()
