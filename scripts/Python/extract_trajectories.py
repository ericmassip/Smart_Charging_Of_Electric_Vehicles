import json
from datetime import date, timedelta
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

for day in days_to_be_checked:
    sessions_of_a_day = df[df.index.dayofyear == pd.Timestamp(day).dayofyear]

    if not sessions_of_a_day.empty:
        sessions_to_be_checked.append(sessions_of_a_day)

print('There are ' + str(len(sessions_to_be_checked)) + ' days with transactions available.')


def save_state_action_tuple(timeslot, Xs, previous_action, day_transactions, state_action_tuples):
    next_timeslot = timeslot + 1

    resulting_Xs = get_resulting_Xs_matrix(Xs, previous_action)
    # Compute cost function
    cost = get_cost(Xs, resulting_Xs, previous_action, 0)
    # Append tuple
    state_action_tuples.append(
        {'timeslot': timeslot, 'Xs': tuple(Xs.flatten() / Nmax), 'us': previous_action, 'next_timeslot': next_timeslot,
         'resulting_Xs': tuple(resulting_Xs.flatten() / Nmax), 'cost': cost})

    if timeslot < Smax:
        resulting_Xs = add_cars_starting_at_this_timeslot(next_timeslot, resulting_Xs, day_transactions)

        Us = get_possible_actions(resulting_Xs)

        # print(Us)

        for next_action in Us:
            save_state_action_tuple(next_timeslot, resulting_Xs, next_action, day_transactions, state_action_tuples)


def filter_state_action_tuples(organized_trajectories):
    state_action_tuples = []
    for traj in random.sample(organized_trajectories, top_sampling_trajectories):
        for state_action_tuple in traj:
            state_action_tuples.append(
                {'timeslot': state_action_tuple.timeslot, 'Xs': tuple(state_action_tuple.Xs.flatten()),
                 'us': state_action_tuple.us, 'next_timeslot': state_action_tuple.next_timeslot,
                 'resulting_Xs': tuple(state_action_tuple.resulting_Xs.flatten()), 'cost': state_action_tuple.cost})
    return state_action_tuples


def save_json_day_trajectories(sessions_of_the_day, top_sampling_trajectories):
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
        save_state_action_tuple(timeslot, Xs, action, day_transactions, state_action_tuples)

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
    f = open('../../../datasets/Trajectories/' + str(top_sampling_trajectories) + '/trajectories_' + day + '.json', "w")
    f.write(json_dump)
    f.close()

    print('Day processed: ' + day)


#save_json_day_trajectories(sessions_to_be_checked[0])

top_sampling_trajectories = 10000

for sessions_of_the_day in sessions_to_be_checked:
    save_json_day_trajectories(sessions_of_the_day, top_sampling_trajectories)
