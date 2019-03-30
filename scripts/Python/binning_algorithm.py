import pandas as pd
import numpy as np
import json

from session_helper import *

sessions = pd.read_csv('~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-03-06.csv')

#sessions_of_the_day = [sessions.loc[7], sessions.loc[8], sessions.loc[9]]
sessions_of_the_day = [sessions.loc[15], sessions.loc[16]]

# The PV obtained from the sun in UTC in Genk in the longest day of the year starts at 6am and ends at 10pm.
# This means that Hmax = 16h. I choose deltaTslot = 2. Then, Smax = 16/2 = 8. Every timeslot will be 2h long.

# Nmax is the maximum number of charging stations available

# Before starting the algorithm for the day, we make sure that the sessions_of_the_day is a dict with the
# timeslot to start for every session and the connection and charging times
day_transactions = get_dict_of_day_transactions(sessions_of_the_day)


def save_state_action_tuple(timeslot, Xs, previous_action):
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

        #print(Us)

        for next_action in Us:
            save_state_action_tuple(next_timeslot, resulting_Xs, next_action)


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
    save_state_action_tuple(timeslot, Xs, action)

json = json.dumps({'trajectories': state_action_tuples})
f = open("dict.json", "w")
f.write(json)
f.close()
