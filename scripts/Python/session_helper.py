import pandas as pd
import numpy as np
import itertools
import functools

start_hour = 6
end_hour = 22
Hmax = end_hour - start_hour
deltaTslot = 2
Smax = int(Hmax/deltaTslot)
Nmax = 6
charging_rate = 1
M = 2 * Nmax


# This method returns a dictionary formed by the sessions' timeslot, time to departure and time to full charge.
# The sessions sent as a parameter should belong to the day being computed
def get_dict_of_day_transactions(sessions):
    day_transactions_dict = []
    for index, row in sessions.iterrows():
        start_time = pd.to_datetime(index)
        connection_time = pd.to_numeric(row['ConnectedTime'])
        charge_time = pd.to_numeric(row['ChargeTime'])

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
    Xs_tmp = Xs
    for transaction in day_transactions:
        if transaction['timeslot'] == timeslot:
            time_to_depart = transaction['time_to_depart'] / deltaTslot
            time_to_full_charge = transaction['time_to_full_charge'] / deltaTslot
            i = int(time_to_depart)
            j = int(time_to_full_charge)
            Xs_tmp[j, i] += 1
    return Xs_tmp


# Returns an array of length Smax where every element is the ratio of cars to be charged, a value between 0 and 1:
# 0 means charge nothing, 1 means charge all of them.
def get_possible_actions_in_diagonal(Xs_total_d):
    number_of_cars_in_the_diagonal = int(Xs_total_d)

    if number_of_cars_in_the_diagonal == 0:
        return [0]
    else:
        return [number_of_cars_to_be_charged/number_of_cars_in_the_diagonal for number_of_cars_to_be_charged in range(0, number_of_cars_in_the_diagonal + 1)]


# Returns an array of length Smax where each element is the amount of cars in the diagonal. Each element corresponds
# to one of the top diagonals. It starts at diagonal 0, until Smax-1
def get_cars_in_upper_diagonals(Xs):
    return [np.sum(np.diagonal(Xs, d)) for d in range(0, Smax)]


# Returns the amount of cars that are on the left edge, hence will disappear after the next timeslot, but they
# haven't been charged so they should still apply for the cost penalty
def get_cars_not_charged_at_the_left_edge(Xs, action):
    cars_in_left_corner = Xs[0, 0]
    cars_not_charged_at_the_left_edge = np.sum(Xs[1:, 0])

    if cars_in_left_corner > 0:
        cars_in_main_diagonal = np.sum(np.diagonal(Xs, 0))
        cars_not_charged_left_corner = cars_in_left_corner - action[0] * cars_in_main_diagonal
        cars_not_charged_at_the_left_edge = cars_not_charged_at_the_left_edge + cars_not_charged_left_corner

    return cars_not_charged_at_the_left_edge


# Returns an array of length Smax where each element is the amount of cars in the diagonal. Each element corresponds
# to one of the low diagonals. It starts at diagonal -1, until Smax-1
def get_cars_in_lower_diagonals(Xs, resulting_Xs, action):
    cars_not_charged_at_the_left_edge = get_cars_not_charged_at_the_left_edge(Xs, action)
    cars_in_lower_diagonals = [np.sum(np.diagonal(resulting_Xs, (-1) * d)) for d in range(1, Smax)]
    return functools.reduce(lambda car1, car2:
                            car1 + car2, cars_in_lower_diagonals) + cars_not_charged_at_the_left_edge


# Return a list with all the possible actions for the given state matrix Xs
def get_possible_actions(Xs):
    above_diagonals = get_cars_in_upper_diagonals(Xs)
    possible_actions_for_every_diagonal = []

    for Xs_total_d in above_diagonals:
        possible_actions_for_every_diagonal.append(get_possible_actions_in_diagonal(Xs_total_d))

    return list(itertools.product(*possible_actions_for_every_diagonal))


# Returns the cost of the given state-action
def get_cost(Xs, resulting_Xs, action, pv_energy_generated):
    cost_demand = get_cost_demand(Xs, action, pv_energy_generated)
    cost_penalty = get_cost_penalty(Xs, resulting_Xs, action)
    return cost_demand + cost_penalty


# Returns the cost of taking the given action on state Xs, also taking into account the PV energy generated
def get_cost_demand(Xs, action, pv_energy_generated):
    cost_of_cars_action = 0
    cars_in_above_diagonals = get_cars_in_upper_diagonals(Xs)

    d = 0
    for cars_in_d in cars_in_above_diagonals:
        cost_of_cars_action += cars_in_d * action[d] * charging_rate
        d += 1

    return (cost_of_cars_action - pv_energy_generated) ** 2


# Returns the penalty cost of having cars in the lower diagonals, which means that those cars will not be fully charged
def get_cost_penalty(Xs, resulting_Xs, action):
    return M * get_cars_in_lower_diagonals(Xs, resulting_Xs, action)


# This method is used for shifting the matrix one position to the left after finishing the timeslot
def shift_left(x):
    y = np.roll(x, -1)
    y[:, Smax - 1] = 0
    return y


def get_resulting_Xs_matrix(Xs, action):
    Xs_to_be_checked = Xs.copy()
    Xs_to_be_changed = np.zeros((Smax, Smax))
    for d in range(0, Smax):
        cols = d
        row = 0
        cars_in_d = np.sum(np.diagonal(Xs_to_be_checked, d))

        # If there are cars in this diagonal, check
        if cars_in_d > 0:
            action_for_d = action[d] * cars_in_d

            # Iterate over the elements of the diagonal d
            for col in range(cols, Smax):
                if action_for_d > 0:
                    cars = int(Xs_to_be_checked[row, col])

                    # If there is at least one car on this element and cars to be charged in this d, proceed
                    if cars > 0:
                        for car in range(1, cars + 1):
                            if action_for_d > 0:
                                if row != 0:
                                    Xs_to_be_changed[row - 1, col] += 1  # Sum 1 to the element on top, because it has been charged
                                Xs_to_be_checked[row, col] -= 1  # Subtract 1 to the current element
                                action_for_d -= 1

                row += 1

    # Shift all elements of the Xs matrix left, because the timeslot is over
    resulting_Xs = shift_left(Xs_to_be_checked) + shift_left(Xs_to_be_changed)

    return resulting_Xs