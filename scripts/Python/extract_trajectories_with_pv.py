import json
from datetime import date, timedelta, datetime
import random
import os
import click

from session_helper import *
from trajectory_helper import StateActionTuple, get_organized_trajectories


def get_pv_generated_that_day(pv_generated_data, day):
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


def save_state_action_tuple(i_day, timeslot, Xs, previous_action, day_transactions, state_action_tuples, pv_per_timeslot_dict):
    next_timeslot = timeslot + 1

    resulting_Xs = get_resulting_Xs_matrix(Xs, previous_action)
    pv_energy_generated = pv_per_timeslot_dict[i_day][timeslot]

    next_pv_energy_generated = 0 if timeslot == Smax else pv_per_timeslot_dict[i_day][next_timeslot]

    # Compute cost function
    cost = get_cost(Xs, resulting_Xs, previous_action, pv_energy_generated)
    # Append tuple
    state_action_tuples.append(
        {'timeslot': timeslot, 'Xs': tuple(Xs.flatten() / Nmax), 'us': previous_action, 'next_timeslot': next_timeslot,
         'resulting_Xs': tuple(resulting_Xs.flatten() / Nmax), 'cost': cost, 'pv': pv_energy_generated, 'next_pv': next_pv_energy_generated})

    if timeslot < Smax:
        resulting_Xs = add_cars_starting_at_this_timeslot(next_timeslot, resulting_Xs, day_transactions)

        Us = get_possible_actions(resulting_Xs)

        for next_action in Us:
            save_state_action_tuple(i_day, next_timeslot, resulting_Xs, next_action, day_transactions, state_action_tuples, pv_per_timeslot_dict)


def filter_state_action_tuples(organized_trajectories, top_sampling_trajectories):
    state_action_tuples = []
    trajectories_to_be_filtered = organized_trajectories

    # If there are more trajectories than the number of samples to be extracted, then get a random number of them.
    if top_sampling_trajectories != 'all' and top_sampling_trajectories.split('_')[0] != 'all':
        top_sampling_trajectories = int(top_sampling_trajectories.split('_')[0]) if '_' in top_sampling_trajectories else int(top_sampling_trajectories)
        if len(organized_trajectories) > top_sampling_trajectories:
            trajectories_to_be_filtered = random.sample(organized_trajectories, top_sampling_trajectories)

    for traj in trajectories_to_be_filtered:
        for state_action_tuple in traj:
            state_action_tuples.append(
                {'timeslot': state_action_tuple.timeslot, 'Xs': tuple(state_action_tuple.Xs.flatten()),
                 'us': state_action_tuple.us, 'next_timeslot': state_action_tuple.next_timeslot,
                 'resulting_Xs': tuple(state_action_tuple.resulting_Xs.flatten()), 'cost': state_action_tuple.cost,
                 'pv': state_action_tuple.pv, 'next_pv': state_action_tuple.next_pv})

    return state_action_tuples


def save_json_day_trajectories(i_day, sessions_of_the_day, top_sampling_trajectories, pv_per_timeslot_dict, trajectories_directory):
    day = sessions_of_the_day.index[0].strftime('%Y-%m-%d')
    day_transactions = get_dict_of_day_transactions(sessions_of_the_day)

    timeslot = 1

    # Initialize Xs with zeros
    Xs = np.zeros((Smax, Smax))

    # Initialize the trajectories array that will save every tuple
    state_action_tuples = []

    # Add cars starting at timeslot 1
    Xs = add_cars_starting_at_this_timeslot(timeslot, Xs, day_transactions)

    # Get the possible actions for this first state at timeslot 1
    Us = get_possible_actions(Xs)

    # Iterate over the possible actions in Us
    for action in Us:
        save_state_action_tuple(i_day, timeslot, Xs, action, day_transactions, state_action_tuples, pv_per_timeslot_dict)

    state_action_tuples_to_be_filtered = [StateActionTuple(state_action) for state_action in state_action_tuples]
    organized_trajectories = get_organized_trajectories(state_action_tuples_to_be_filtered)
    print('Original number of trajectories = ' + str(len(organized_trajectories)))

    state_action_tuples = filter_state_action_tuples(organized_trajectories, top_sampling_trajectories)

    state_action_tuples_to_be_filtered = [StateActionTuple(state_action) for state_action in state_action_tuples]
    organized_trajectories = get_organized_trajectories(state_action_tuples_to_be_filtered)
    print('Reduced number of trajectories = ' + str(len(organized_trajectories)))

    json_dump = json.dumps({'trajectories': state_action_tuples})

    if not os.path.exists(trajectories_directory):
        os.makedirs(trajectories_directory)

    f = open(trajectories_directory + str(top_sampling_trajectories) + '/trajectories_' + day + '.json', "w")
    f.write(json_dump)
    f.close()

    print('Day processed: ' + day)


@click.command()
@click.option(
    '--sessions',
    type=click.STRING,
    required=True,
    help='Sessions file with the historical transactions to be used.'
)
@click.option(
    '--tpc_file',
    type=click.STRING,
    required=True,
    help='Path to the file where the total power consumption is saved.'
)
@click.option(
    '--trajectories_path',
    type=click.STRING,
    required=True,
    help='Path to the file where the trajectories will be saved.'
)
@click.option(
    '--tst',
    type=click.STRING,
    default='all',
    required=False,
    help="Top sampling trajectories: Specify a value for the amount of random trajectories to be extracted. Say 'all' "
         "to extract all the possible trajectories of the decision tree, or a number like 5000 or 10000 or 15000."
)
def extract_trajectories(sessions, tpc_file, trajectories_path, tst):
    start_day = date(2018, 8, 1)
    end_day = date(2019, 8, 1)

    delta = end_day - start_day

    days_to_be_checked = [start_day + timedelta(i) for i in range(delta.days)]

    sessions_to_be_checked = []
    #sessions_filename = '~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-05-05.csv'
    sessions_filename = sessions
    sessions = pd.read_csv(sessions_filename, index_col='Started')
    df = sessions
    df.index = pd.to_datetime(df.index)

    #tpc_file = '~/Projects/MAI/Thesis/datasets/PV/total_power_consumption_2019-05-05.csv'
    pv_generated_data = pd.read_csv(tpc_file)

    pv_per_timeslot_dict = []

    for day in days_to_be_checked:
        sessions_of_a_day = df[df.index.dayofyear == pd.Timestamp(day).dayofyear]

        if not sessions_of_a_day.empty:
            sessions_to_be_checked.append(sessions_of_a_day)

            pv_in_that_day = get_pv_generated_that_day(pv_generated_data, day)
            pv_per_timeslot_dict.append(pv_in_that_day)

    print('There are ' + str(len(sessions_to_be_checked)) + ' days with transactions available.')

    #trajectories_directory = '../../../datasets/Trajectories/'
    trajectories_directory = trajectories_path
    #top_sampling_trajectories = 'all'
    top_sampling_trajectories = tst

    for i_day in range(len(sessions_to_be_checked)):
        sessions_of_the_day = sessions_to_be_checked[i_day]
        save_json_day_trajectories(i_day, sessions_of_the_day, top_sampling_trajectories, pv_per_timeslot_dict, trajectories_directory)


if __name__ == '__main__':
    extract_trajectories()
