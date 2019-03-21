import pandas as pd
import numpy as np
import json

import session_helper

sessions = pd.read_csv('~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-03-06.csv')

# sessions_of_the_day = [sessions.loc[14], sessions.loc[15], sessions.loc[16]]
sessions_of_the_day = [sessions.loc[15], sessions.loc[16]]

# The PV obtained from the sun in UTC in Genk in the longest day of the year starts at 6am and ends at 10pm.
# This means that Hmax = 16h. I choose deltaTslot = 2. Then, Smax = 16/2 = 8. Every timeslot will be 2h long.
Smax = session_helper.Smax
deltaTslot = session_helper.deltaTslot
start_hour = session_helper.start_hour
end_hour = session_helper.end_hour

# Nmax is the maximum number of charging stations available
Nmax = session_helper.Nmax

# Before starting the algorithm for the day, we make sure that the sessions_of_the_day is a dict with the
# timeslot to start for every session and the connection and charging times
day_transactions = session_helper.get_dict_of_day_transactions(sessions_of_the_day)


def shift_left(x):
    y = np.roll(x, -1)
    y[:, Smax - 1] = 0
    return y


def add_cars_starting_at_this_timeslot(timeslot, Xs):
    Xs_tmp = Xs * Nmax
    for transaction in day_transactions:
        if transaction['timeslot'] == timeslot:
            time_to_depart = transaction['time_to_depart'] / deltaTslot
            time_to_full_charge = transaction['time_to_full_charge'] / deltaTslot
            i = int(time_to_depart)
            j = int(time_to_full_charge)
            Xs_tmp[j, i] += 1
    return Xs_tmp / Nmax


def get_resulting_Xs_matrix(timeslot, Xs, action):
    Xs_tmp = Xs * Nmax

    for d in range(0, Smax):
        cols = d
        row = 0
        cars_in_d = np.sum(np.diagonal(Xs_tmp, d))

        # If there are cars in this diagonal, check
        if cars_in_d > 0:
            action_for_d = action[d] * cars_in_d

            # Iterate over the elements of the diagonal d
            for col in range(cols, Smax):
                if action_for_d > 0:
                    cars = int(Xs_tmp[row, col])

                    # If there is at least one car on this element and cars to be charged in this d, proceed
                    if cars > 0 and action_for_d > 0:
                        for car in range(1, cars + 1):
                            if action_for_d > 0:
                                Xs_tmp[row - 1, col] += 1  # Sum 1 to the element on top, because it has been charged
                                Xs_tmp[row, col] -= 1  # Subtract 1 to the current element
                                action_for_d -= 1

                row += 1

    # Shift all elements of the Xs matrix left, because the timeslot is over
    if timeslot > 1:
        Xs_tmp = shift_left(Xs_tmp)

    return Xs_tmp / Nmax


def save_state_action_tuple(timeslot, Xs, previous_action, trajectory):
    next_timeslot = timeslot + 1

    resulting_Xs = get_resulting_Xs_matrix(next_timeslot, Xs, previous_action)
    # Compute cost function
    cost = 1000
    # Append tuple
    trajectory.append(
        {'timeslot': timeslot, 'Xs': tuple(Xs.flatten()), 'us': previous_action, 'next_timeslot': next_timeslot,
         'resulting_Xs': tuple(resulting_Xs.flatten()), 'cost': cost})

    if timeslot < Smax:
        resulting_Xs = add_cars_starting_at_this_timeslot(next_timeslot, resulting_Xs)

        Us = session_helper.get_possible_actions(resulting_Xs)

        for next_action in Us:
            save_state_action_tuple(next_timeslot, resulting_Xs, next_action, trajectory)
    else:
        state_action_tuples.append(trajectory)


timeslot = 1

# Initialize Xs with zeros
Xs = np.zeros((Smax, Smax))

# Initialize the trajectories array that will save every tuple
state_action_tuples = []

# Add cars starting at timeslot 1
Xs = add_cars_starting_at_this_timeslot(timeslot, Xs)

# Get the possible actions for this first state at timeslot 1
Us = session_helper.get_possible_actions(Xs)

# Iterate over the possible actions in Us
for action in Us:
    trajectory = []
    save_state_action_tuple(timeslot, Xs, action, trajectory)

json = json.dumps({'trajectories': state_action_tuples})
f = open("dict.json", "w")
f.write(json)
f.close()
