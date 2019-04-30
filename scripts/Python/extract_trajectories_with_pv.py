import json
from datetime import date, timedelta, datetime
import random

from session_helper import *
from trajectory_helper import StateActionTuple, get_organized_trajectories

start_day = date(2018, 7, 1)
end_day = date(2019, 5, 1)

delta = end_day - start_day
timedelta_1_day = timedelta(days=1)

days_to_be_checked = [start_day + timedelta(i) for i in range(delta.days)]

sessions_to_be_checked = []
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

for day in days_to_be_checked:
    sessions_of_a_day = df[df.index.dayofyear == pd.Timestamp(day).dayofyear]

    if not sessions_of_a_day.empty:
        sessions_to_be_checked.append(sessions_of_a_day)

        pv_in_that_day = get_pv_generated_that_day(day)
        pv_per_timeslot_dict.append(pv_in_that_day)

print('There are ' + str(len(sessions_to_be_checked)) + ' days with transactions available.')


def save_state_action_tuple(i_day, timeslot, Xs, previous_action, day_transactions, state_action_tuples):
    next_timeslot = timeslot + 1

    resulting_Xs = get_resulting_Xs_matrix(Xs, previous_action)
    pv_energy_generated = pv_per_timeslot_dict[i_day][timeslot]

    # Compute cost function
    cost = get_cost(Xs, resulting_Xs, previous_action, pv_energy_generated)
    # Append tuple
    state_action_tuples.append(
        {'timeslot': timeslot, 'Xs': tuple(Xs.flatten() / Nmax), 'us': previous_action, 'next_timeslot': next_timeslot,
         'resulting_Xs': tuple(resulting_Xs.flatten() / Nmax), 'cost': cost})

    if timeslot < Smax:
        resulting_Xs = add_cars_starting_at_this_timeslot(next_timeslot, resulting_Xs, day_transactions)

        Us = get_possible_actions(resulting_Xs)

        # print(Us)

        for next_action in Us:
            save_state_action_tuple(i_day, next_timeslot, resulting_Xs, next_action, day_transactions, state_action_tuples)


def filter_state_action_tuples(organized_trajectories):
    state_action_tuples = []
    for traj in random.sample(organized_trajectories, top_sampling_trajectories):
        for state_action_tuple in traj:
            state_action_tuples.append(
                {'timeslot': state_action_tuple.timeslot, 'Xs': tuple(state_action_tuple.Xs.flatten()),
                 'us': state_action_tuple.us, 'next_timeslot': state_action_tuple.next_timeslot,
                 'resulting_Xs': tuple(state_action_tuple.resulting_Xs.flatten()), 'cost': state_action_tuple.cost})

    return state_action_tuples


def save_json_day_trajectories(i_day, sessions_of_the_day, top_sampling_trajectories):
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
        save_state_action_tuple(i_day, timeslot, Xs, action, day_transactions, state_action_tuples)

    if top_sampling_trajectories != 'all':
        state_action_tuples_filtered = [StateActionTuple(state_action) for state_action in state_action_tuples]
        organized_trajectories = get_organized_trajectories(state_action_tuples_filtered)
        print('Original number of trajectories = ' + str(len(organized_trajectories)))
        if len(organized_trajectories) > top_sampling_trajectories:
            state_action_tuples = filter_state_action_tuples(organized_trajectories)

    state_action_tuples_filtered = [StateActionTuple(state_action) for state_action in state_action_tuples]
    organized_trajectories = get_organized_trajectories(state_action_tuples_filtered)
    print('Reduced number of trajectories = ' + str(len(organized_trajectories)))

    json_dump = json.dumps({'trajectories': state_action_tuples})
    f = open('../../../datasets/Trajectories/PV/' + str(top_sampling_trajectories) + '/trajectories_' + day + '.json', "w")
    f.write(json_dump)
    f.close()

    print('Day processed: ' + day)


#save_json_day_trajectories(sessions_to_be_checked[0])

top_sampling_trajectories = 5000

for i_day in range(len(sessions_to_be_checked)):
    sessions_of_the_day = sessions_to_be_checked[i_day]
    save_json_day_trajectories(i_day, sessions_of_the_day, top_sampling_trajectories)
