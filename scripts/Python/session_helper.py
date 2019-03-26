import pandas as pd
import numpy as np
import itertools

start_hour = 6
end_hour = 12
Hmax = end_hour - start_hour
deltaTslot = 2
Smax = int(Hmax/deltaTslot)
Nmax = 3


# This method returns a dictionary formed by the sessions' timeslot, time to departure and time to full charge.
# The sessions sent as a parameter should belong to the day being computed
def get_dict_of_day_transactions(sessions):
    day_transactions_dict = []
    for session in sessions:
        start_time = pd.to_datetime(session['Started'])
        connection_time = pd.to_numeric(session['ConnectedTime'])
        charge_time = pd.to_numeric(session['ChargeTime'])

        session_start_timeslot = get_session_start_timeslot(start_time)

        day_transactions_dict.append({'timeslot': session_start_timeslot,
                                      'time_to_depart': connection_time,
                                      'time_to_full_charge': charge_time})

    return day_transactions_dict


# Given the starting time of the session, this method returns the timeslot in which the session is starting
def get_session_start_timeslot(start_time):
    hour_of_next_timeslot = start_hour + deltaTslot
    session_start_timeslot = 1
    found = False

    while not found:
        if start_time.hour < hour_of_next_timeslot or session_start_timeslot == Smax:
            found = True
        else:
            hour_of_next_timeslot += deltaTslot
            session_start_timeslot += 1

    return session_start_timeslot


# Return a normalized matrix adding the cars starting their charging at this timeslot
def add_cars_starting_at_this_timeslot(timeslot, Xs, day_transactions):
    Xs_tmp = Xs * Nmax
    for transaction in day_transactions:
        if transaction['timeslot'] == timeslot:
            time_to_depart = transaction['time_to_depart'] / deltaTslot
            time_to_full_charge = transaction['time_to_full_charge'] / deltaTslot
            i = int(time_to_depart)
            j = int(time_to_full_charge)
            Xs_tmp[j, i] += 1
    return Xs_tmp / Nmax


# Returns an array of length Smax where every element is the ratio of cars to be charged, a value between 0 and 1:
# 0 means charge nothing, 1 means charge all of them.
def get_possible_actions_in_diagonal(Xs_total_d):
    number_of_cars_in_the_diagonal = int(Xs_total_d * Nmax)

    if number_of_cars_in_the_diagonal == 0:
        return [0]
    else:
        return [number_of_cars_to_be_charged/number_of_cars_in_the_diagonal for number_of_cars_to_be_charged in range(0, number_of_cars_in_the_diagonal + 1)]


# Returns an array of length Smax where each element is the amount of cars in the diagonal. Each element corresponds
# to one of the top diagonals. It starts at diagonal 0, until Smax-1
def get_above_diagonals(Xs):
    return [np.sum(np.diagonal(Xs, d)) for d in range(0, Smax)]


# Returns an array of length Smax where each element is the amount of cars in the diagonal. Each element corresponds
# to one of the low diagonals. It starts at diagonal -1, until Smax-1
def get_lower_diagonals(Xs):
    return [np.sum(np.diagonal(Xs, (-1)*d)) for d in range(1, Smax)]


# Return a list with all the possible actions for the given state matrix Xs
def get_possible_actions(Xs):
    above_diagonals = get_above_diagonals(Xs)
    possible_actions_for_every_diagonal = []

    for Xs_total_d in above_diagonals:
        possible_actions_for_every_diagonal.append(get_possible_actions_in_diagonal(Xs_total_d))

    return list(itertools.product(*possible_actions_for_every_diagonal))


# Returns the cost of the given state-action
def get_cost(Xs, action, pv_energy_generated):
    cost_demand = get_cost_demand(Xs, action, pv_energy_generated)
    cost_penalty = get_cost_penalty(Xs)
    return cost_demand + cost_penalty


# Returns the cost of taking the given action on state Xs, also taking into account the PV energy generated
def get_cost_demand(Xs, action, pv_energy_generated):
    cost_of_cars_action = 0
    cars_in_above_diagonals = get_above_diagonals(Xs)

    d = 0
    for cars_in_d in cars_in_above_diagonals:
        cost_of_cars_action += cars_in_d * action[d]
        d += 1

    return (cost_of_cars_action - pv_energy_generated) ** 2


# Returns the penalty cost of having cars in the lower diagonals, which means that those cars will not be fully charged
def get_cost_penalty(Xs):
    M = 2 * Nmax
    cost_penalty = 0
    cars_in_lower_diagonals = get_lower_diagonals(Xs)

    for cars_in_minus_d in cars_in_lower_diagonals:
        cost_penalty += cars_in_minus_d

    return M * cost_penalty


# This method is used for shifting the matrix one position to the left after finishing the timeslot
def shift_left(x):
    y = np.roll(x, -1)
    y[:, Smax - 1] = 0
    return y


def get_resulting_Xs_matrix(timeslot, Xs, action):
    Xs_tmp = Xs * Nmax
    Xs_tmp2 = Xs_tmp
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
                                if row != 0:
                                    Xs_tmp[row - 1, col] += 1  # Sum 1 to the element on top, because it has been charged
                                Xs_tmp[row, col] -= 1  # Subtract 1 to the current element
                                action_for_d -= 1

                row += 1

    # Shift all elements of the Xs matrix left, because the timeslot is over
    if timeslot > 1:
        Xs_tmp = shift_left(Xs_tmp)

    return Xs_tmp / Nmax