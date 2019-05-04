import json
import glob
import pandas as pd
import tensorflow as tf
import numpy as np
import logging
from datetime import timedelta, datetime

from keras.models import load_model

import keras.losses
keras.losses.huber_loss = tf.losses.huber_loss

from session_helper import *
import trajectory_helper


# Now get the optimal cost of the day iterating over all the possible trajectories
# and saving the cost of the one with lower accumulated cost
def get_optimal_cost(day_trajectories):
    state_actions = json.loads(open(day_trajectories).read())['trajectories']
    state_action_tuples = [trajectory_helper.StateActionTuple(state_action) for state_action in state_actions]

    organized_trajectories = trajectory_helper.get_organized_trajectories(state_action_tuples)
    accumulated_costs = [trajectory_helper.get_accumulated_cost(trajectory) for trajectory in organized_trajectories]

    return min(accumulated_costs)


# Calculate the cost of the day charging everything all the time (Business As Usual)
def get_BAU_cost(i_day, sessions_of_the_day):
    BAU_cost_day = 0
    day_transactions = get_dict_of_day_transactions(sessions_of_the_day)
    BAU_default_action = np.ones(Smax)

    Xs = np.zeros((Smax, Smax))

    for timeslot in range(1, Smax + 1):
        Xs = add_cars_starting_at_this_timeslot(timeslot, Xs, day_transactions)

        resulting_Xs = get_resulting_Xs_matrix(Xs, BAU_default_action)

        pv_energy_generated = pv_per_timeslot_dict[i_day][timeslot]
        BAU_cost_day += get_cost(Xs, resulting_Xs, BAU_default_action, pv_energy_generated)
        Xs = resulting_Xs.copy()

    return BAU_cost_day


def get_action_with_minimum_q_value(i_day, timeslot, Xs):
    next_timeslot = timeslot + 1
    possible_actions = get_possible_actions(Xs)
    model = approximated_functions.get(timeslot)

    q_values_for_possible_actions = {}
    for action in possible_actions:
        resulting_Xs = get_resulting_Xs_matrix(Xs, action)
        q_value = predict(i_day, next_timeslot, resulting_Xs, action, model)
        q_values_for_possible_actions.update({action: q_value[0][0]})

    return min(q_values_for_possible_actions, key=q_values_for_possible_actions.get)


def predict(i_day, next_timeslot, resulting_Xs, action, previous_Q_approximated_function):
    next_pv_energy_generated = 0 if next_timeslot > Smax else pv_per_timeslot_dict[i_day][next_timeslot]
    input_value = np.array([next_pv_energy_generated, *action, *resulting_Xs.flatten()])
    return previous_Q_approximated_function.predict(np.reshape(input_value, (1, len(input_value))))


# Calculate the cost of the day following policy decisions
def get_policy_cost(i_day, sessions_of_the_day):
    policy_cost_day = 0
    day_transactions = get_dict_of_day_transactions(sessions_of_the_day)

    Xs = np.zeros((Smax, Smax))

    for timeslot in range(1, Smax + 1):
        Xs = add_cars_starting_at_this_timeslot(timeslot, Xs, day_transactions)

        policy_action = get_action_with_minimum_q_value(i_day, timeslot, Xs)
        resulting_Xs = get_resulting_Xs_matrix(Xs, policy_action)

        pv_energy_generated = pv_per_timeslot_dict[i_day][timeslot]
        policy_cost_day += get_cost(Xs, resulting_Xs, policy_action, pv_energy_generated)
        Xs = resulting_Xs.copy()

    return policy_cost_day

n_epochs = 1
batch_size = 64
loss = 'huber'
samples = '5000'
models_directory = '../../../models/PV/PV_samples_' + str(samples) + '_n_epochs_' + str(n_epochs) + '_batch_size_' + str(batch_size) + '_loss_' + loss + '/'

# Logfile to save the info about the testing. The 'w' filemode re-writes the file every time.
# If you prefer to keep all the run results on the log file, remove filemode='w'
logging.basicConfig(filename=models_directory + 'evaluation_function.log', level=logging.INFO, filemode='w')

Q1_approximated_function = load_model(models_directory + 'Q1_approximated_function.h5')
Q2_approximated_function = load_model(models_directory + 'Q2_approximated_function.h5')
Q3_approximated_function = load_model(models_directory + 'Q3_approximated_function.h5')
Q4_approximated_function = load_model(models_directory + 'Q4_approximated_function.h5')
Q5_approximated_function = load_model(models_directory + 'Q5_approximated_function.h5')
Q6_approximated_function = load_model(models_directory + 'Q6_approximated_function.h5')
Q7_approximated_function = load_model(models_directory + 'Q7_approximated_function.h5')
Q8_approximated_function = load_model(models_directory + 'Q8_approximated_function.h5')

approximated_functions = {
    1: Q1_approximated_function,
    2: Q2_approximated_function,
    3: Q3_approximated_function,
    4: Q4_approximated_function,
    5: Q5_approximated_function,
    6: Q6_approximated_function,
    7: Q7_approximated_function,
    8: Q8_approximated_function
}

samples_all = 'all'
day_trajectories = sorted(glob.glob("/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/" + samples_all + "/*.json"))
test_day_trajectories = []
for i_day in range(len(day_trajectories)):
    if i_day != 0 and i_day % 5 == 0:
        test_day_trajectories.append(day_trajectories[i_day])

test_day_sessions = []
sessions = pd.read_csv('~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-04-25.csv', index_col='Started')
df = sessions
df.index = pd.to_datetime(df.index)

pv_generated_data = pd.read_csv('~/Projects/MAI/Thesis/datasets/PV/total_power_consumption.csv')


def get_pv_generated_that_day(day):
    timedelta_15 = timedelta(minutes=15)

    start_time = datetime(day.year, day.month, day.day, start_hour, 0, 0)

    pv_per_timeslot = {}
    date = start_time

    for timeslot in range(1, Smax + 1):
        pv_this_timeslot = 0
        for i in range(deltaTslot):
            pv_this_hour = 0
            for j in range(4): # 4 because there are 15min every hour
                # Get PV data for that exact hour
                pv_generated_now = pv_generated_data[pv_generated_data['date'] == date.strftime("%Y-%m-%d %H:%M:%S")]['power_sum'].values[0] / 1000
                pv_this_hour += pv_generated_now
                date += timedelta_15

            pv_this_timeslot += pv_this_hour / 4

        scaled_pv_this_timeslot = pv_this_timeslot * pv_scale
        pv_per_timeslot.update({timeslot: scaled_pv_this_timeslot})

    return pv_per_timeslot


pv_per_timeslot_dict = []

for day in test_day_trajectories:
    sessions_of_a_day = df[df.index.dayofyear == pd.Timestamp(day[-15:-5]).dayofyear]

    if not sessions_of_a_day.empty:
        test_day_sessions.append(sessions_of_a_day)

        pv_in_that_day = get_pv_generated_that_day(pd.to_datetime(day[-15:-5]))
        pv_per_timeslot_dict.append(pv_in_that_day)

print('')
print('There are ' + str(len(test_day_sessions)) + ' testing days.')

#test_day_trajectories = test_day_trajectories[0:4] # This line is just for testing!! Otherwise COMMENT or REMOVE.

relative_cost_BAU = 0
relative_cost_policy = 0

times_BAU_better = 0
times_policy_better = 0
draws = 0

#for i_day in range(len(test_day_trajectories)):
#for i_day in [10, 14, 15, 16]:
for i_day in [14]:
    day_sessions = test_day_sessions[i_day]
    day_trajectories = test_day_trajectories[i_day]

    BAU_cost_day = get_BAU_cost(i_day, day_sessions)
    policy_cost_day = get_policy_cost(i_day, day_sessions)
    optimal_cost_day = get_optimal_cost(day_trajectories)

    if BAU_cost_day > policy_cost_day:
        times_policy_better += 1
    elif policy_cost_day > BAU_cost_day:
        times_BAU_better += 1
    else:
        draws += 1

    if BAU_cost_day < 0 or policy_cost_day < 0 or optimal_cost_day < 0:
        logging.warning('A cost day smaller than 0 was found in the test trajectory ' + str(i_day) + '.')

    logging.info('Test trajectory ' + str(i_day) +
                 ' - BAU     cost = ' + str(BAU_cost_day))
    logging.info('Test trajectory ' + str(i_day) +
                 ' - Policy  cost = ' + str(policy_cost_day))
    logging.info('Test trajectory ' + str(i_day) +
                 ' - Optimal cost = ' + str(optimal_cost_day))
    logging.info('')

    relative_cost_BAU += BAU_cost_day / optimal_cost_day
    relative_cost_policy += policy_cost_day / optimal_cost_day

relative_error_given_BAU = relative_cost_BAU / len(test_day_trajectories)
relative_error_given_policy = relative_cost_policy / len(test_day_trajectories)

logging.info('Times BAU better = ' + str(times_BAU_better))
logging.info('Times Policy better = ' + str(times_policy_better))

logging.info('')

logging.info('Relative error BAU = ' + str(round(relative_error_given_BAU, 2)))
logging.info('Relative error given policy = ' + str(round(relative_error_given_policy, 2)))

print('')
print('Times BAU better = ' + str(times_BAU_better))
print('Times Policy better = ' + str(times_policy_better))
print('')
print('Relative error BAU = ' + str(round(relative_error_given_BAU, 2)))
print('Relative error given policy = ' + str(round(relative_error_given_policy, 2)))