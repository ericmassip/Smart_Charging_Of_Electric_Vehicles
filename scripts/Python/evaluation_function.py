import pandas as pd
import numpy as np
import json

from session_helper import *
import trajectory_helper

sessions = pd.read_csv('~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-03-06.csv')
#sessions_of_the_day = [sessions.loc[1], sessions.loc[2], sessions.loc[3]]
sessions_of_the_day = [sessions.loc[15], sessions.loc[16]]

testing_days = [sessions_of_the_day]


def get_relative_error_given_BAU(testing_days):
    relative_cost = 0

    for day in testing_days:
        BAU_cost_day = get_BAU_cost(day)
        optimal_cost_day = get_optimal_cost()
        relative_cost += BAU_cost_day / optimal_cost_day

    return relative_cost / len(testing_days)


def get_relative_error_given_policy(testing_days):
    relative_cost = 0

    for day in testing_days:
        policy_cost_day = get_policy_cost(day)
        optimal_cost_day = get_optimal_cost()
        relative_cost += policy_cost_day / optimal_cost_day

    return relative_cost / len(testing_days)


def get_relative_error(testing_days, given_cost_day):
    relative_cost = 0

    for day in testing_days:
        optimal_cost_day = get_optimal_cost()

        relative_cost += given_cost_day / optimal_cost_day

    return relative_cost / len(testing_days)


# Now get the optimal cost of the day iterating over all the possible trajectories
# and saving the cost of the one with lower accumulated cost
def get_optimal_cost():
    json_to_be_beautified = json.loads(open('dict.json').read())
    state_actions = json_to_be_beautified['trajectories']
    state_action_tuples = [trajectory_helper.StateActionTuple(state_action) for state_action in state_actions]

    organized_trajectories = trajectory_helper.get_organized_trajectories(state_action_tuples)
    #trajectory_helper.show_organized_trajectories(organized_trajectories)
    accumulated_costs = [trajectory_helper.get_accumulated_cost(trajectory) for trajectory in organized_trajectories]
    return min(accumulated_costs)


# Calculate the cost of the day following policy decisions
def get_policy_cost(sessions_of_the_day):
    policy_cost_day = 0
    day_transactions = get_dict_of_day_transactions(sessions_of_the_day)

    Xs = np.zeros((Smax, Smax))

    for timeslot in range(1, Smax + 1):
        Xs = add_cars_starting_at_this_timeslot(timeslot, Xs, day_transactions)
        Us = get_possible_actions(Xs)
        next_timeslot = timeslot + 1

        # TODO: Iterate over the possible actions to take and choose the one with lowest Q-value
        policy_action = []
        Xs = get_resulting_Xs_matrix(next_timeslot, Xs, policy_action)

        pv_energy_generated = 0
        policy_cost_day += get_cost(Xs, policy_action, pv_energy_generated)

    return policy_cost_day


# Calculate the cost of the day charging everything all the time (Business As Usual)
def get_BAU_cost(sessions_of_the_day):
    BAU_cost_day = 0
    day_transactions = get_dict_of_day_transactions(sessions_of_the_day)

    Xs = np.zeros((Smax, Smax))

    for timeslot in range(1, Smax + 1):
        Xs = add_cars_starting_at_this_timeslot(timeslot, Xs, day_transactions)
        BAU_action = np.ones(Smax)
        next_timeslot = timeslot + 1

        Xs = get_resulting_Xs_matrix(next_timeslot, Xs, BAU_action)

        pv_energy_generated = 0
        BAU_cost_day += get_cost(Xs, BAU_action, pv_energy_generated)

    return BAU_cost_day


print('Optimal cost: ' + str(get_optimal_cost()))
print('BAU cost: ' + str(get_BAU_cost(sessions_of_the_day)))