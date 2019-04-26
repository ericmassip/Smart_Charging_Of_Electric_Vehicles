import unittest
import numpy as np
from session_helper import get_resulting_Xs_matrix, get_cost, charging_rate, M

# For testing with Smax = 3, start_hour = 6 and end_hour = 12

class StateActionTuples(unittest.TestCase):

    def test_nothing_charging(self):
        Xs = np.array([[0, 0, 0],
                       [0, 0, 0],
                       [0, 0, 0]])

        action = np.array([0, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = 0

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_all_charging(self):
        Xs = np.array([[0, 0, 0],
                       [0, 0, 0],
                       [0, 0, 0]])

        action = np.array([1, 1, 1])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = 0

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_nothing_charging_with_1_car_in_the_center(self):
        Xs = np.array([[0, 0, 0],
                       [0, 1, 0],
                       [0, 0, 0]])

        action = np.array([0, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [1, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = M * 1

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_nothing_charging_with_1_car_at_the_edge(self):
        Xs = np.array([[0, 0, 0],
                       [1, 0, 0],
                       [0, 0, 0]])

        action = np.array([0, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = M * 1

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_nothing_charging_with_cars_1(self):
        Xs = np.array([[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]])

        action = np.array([0, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [1, 0, 0],
                                          [0, 1, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = M * 3

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_nothing_charging_with_cars_2(self):
        Xs = np.array([[0, 1, 0],
                       [0, 1, 1],
                       [0, 0, 0]])

        action = np.array([0, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[1, 0, 0],
                                          [1, 1, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = M * 1

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_nothing_charging_with_cars_3(self):
        Xs = np.array([[1, 0, 0],
                       [1, 0, 0],
                       [0, 1, 0]])

        action = np.array([0, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [1, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = M * 3

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_nothing_charging_with_cars_4(self):
        Xs = np.array([[1, 1, 1],
                       [0, 0, 0],
                       [0, 0, 0]])

        action = np.array([0, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[1, 1, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = M * 1

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_1_car_center(self):
        Xs = np.array([[0, 0, 0],
                       [0, 1, 0],
                       [0, 0, 0]])

        action = np.array([1, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[1, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (1 * 1 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_1_car_edge(self):
        Xs = np.array([[0, 1, 0],
                       [0, 0, 0],
                       [0, 0, 0]])

        action = np.array([0, 1, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (1 * 1 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_2_cars_same_diagonal(self):
        Xs = np.array([[0, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]])

        action = np.array([1, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[1, 0, 0],
                                          [0, 1, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (2 * 1 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_2_cars_same_diagonal_2(self):
        Xs = np.array([[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 0]])

        action = np.array([1, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[1, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (2 * 1 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_half_cars_same_diagonal(self):
        Xs = np.array([[2, 0, 0],
                       [0, 0, 0],
                       [0, 0, 0]])

        action = np.array([0.5, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (2 * 0.5 * charging_rate)**2 + M * 1

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_half_cars_same_diagonal_with_extra_car(self):
        Xs = np.array([[2, 0, 0],
                       [0, 1, 0],
                       [0, 0, 0]])

        action = np.array([(1/3), 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [1, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (3 * (1/3) * charging_rate)**2 + M * 2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_all_cars_same_diagonal_with_extra_car(self):
        Xs = np.array([[2, 0, 0],
                       [0, 1, 0],
                       [0, 0, 0]])

        action = np.array([1, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[1, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (3 * 1 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_2_cars_same_diagonal_1_edge(self):
        Xs = np.array([[0, 1, 0],
                       [0, 0, 1],
                       [0, 0, 0]])

        action = np.array([0, 1, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 1, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (2 * 1 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_2_cars_different_diagonal(self):
        Xs = np.array([[0, 0, 0],
                       [0, 1, 1],
                       [0, 0, 0]])

        action = np.array([1, 1, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[1, 1, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = ((1 * 1 * charging_rate) * 2)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_half_the_cars_1(self):
        Xs = np.array([[0, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]])

        action = np.array([0.5, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[1, 0, 0],
                                          [0, 0, 0],
                                          [0, 1, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (2 * 0.5 * charging_rate)**2 + M * 1

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_half_the_cars_2(self):
        Xs = np.array([[0, 1, 0],
                       [0, 0, 1],
                       [0, 0, 0]])

        action = np.array([0, 0.5, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 1, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (2 * 0.5 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_half_the_cars_3(self):
        Xs = np.array([[0, 0, 0],
                       [0, 0, 2],
                       [0, 0, 0]])

        action = np.array([0, 0.5, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 1, 0],
                                          [0, 1, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (2 * 0.5 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_half_the_cars_4(self):
        Xs = np.array([[0, 1, 0],
                       [0, 1, 0],
                       [0, 0, 0]])

        action = np.array([1, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[2, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (1 * 1 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_not_charging_left_corner(self):
        Xs = np.array([[1, 0, 0],
                       [0, 0, 0],
                       [1, 0, 0]])

        action = np.array([0, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = M * 2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_charging_left_corner(self):
        Xs = np.array([[1, 0, 0],
                       [0, 0, 0],
                       [0, 0, 0]])

        action = np.array([1, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (1 * 1 * charging_rate)**2

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)

    def test_half_charging_left_corner(self):
        Xs = np.array([[2, 0, 0],
                       [0, 0, 0],
                       [0, 0, 0]])

        action = np.array([0.5, 0, 0])

        actual_resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        expected_resulting_Xs = np.array([[0, 0, 0],
                                          [0, 0, 0],
                                          [0, 0, 0]])

        actual_cost = get_cost(Xs, actual_resulting_Xs, action, 0)
        expected_cost = (2 * 0.5 * charging_rate)**2 + M * 1

        self.assertTrue(np.array_equal(actual_resulting_Xs, expected_resulting_Xs))
        self.assertEqual(expected_cost, actual_cost)


if __name__ == '__main__':
    unittest.main()
