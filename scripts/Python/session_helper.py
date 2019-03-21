import pandas as pd
import numpy as np
import itertools

start_hour = 6
end_hour = 12
Hmax = end_hour - start_hour
deltaTslot = 2
Smax = int(Hmax/deltaTslot)
Nmax = 3


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


def add_transactions_starting_in_this_tslot(timeslot, day_transactions, F):
    for transaction in day_transactions:
        if transaction['timeslot'] == timeslot:
            F.append(transaction)
    return F


# At the end of every iteration, the sessions with ConnectedTime == 0 must be erased because they are not connected
# anymore
def get_pruned_sessions(F):
    for session in F:
        if session['time_to_depart'] == 0:
            F.remove(session)
    return F


def get_possible_actions_in_diagonal(Xs_total_d):
    number_of_cars_in_the_diagonal = int(np.ceil(Xs_total_d))

    if number_of_cars_in_the_diagonal == 0:
        return [0]
    else:
        return [number_of_cars_to_be_charged/number_of_cars_in_the_diagonal for number_of_cars_to_be_charged in range(0, number_of_cars_in_the_diagonal + 1)]


def get_diagonals(Xs):
    return [np.sum(np.diagonal(Xs, d)) for d in range(0, Smax)]


def get_possible_actions(Xs):
    above_diagonals = get_diagonals(Xs)
    possible_actions_for_every_diagonal = []

    for Xs_total_d in above_diagonals:
        possible_actions_for_every_diagonal.append(get_possible_actions_in_diagonal(Xs_total_d))

    return list(itertools.product(*possible_actions_for_every_diagonal))