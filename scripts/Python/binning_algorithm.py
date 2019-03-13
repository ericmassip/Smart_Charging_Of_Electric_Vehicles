import pandas as pd
import numpy as np
import datetime

sessions = pd.read_csv('~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-03-06.csv')

sessions_of_the_day = [sessions.loc[0], sessions.loc[1], sessions.loc[2]]

# The PV obtained from the sun in UTC in Genk in the longest day of the year starts at 6am and ends at 10pm.
# This means that Hmax = 16h. I choose deltaTslot = 1. Then, Smax = 16/1 = 16. Every timeslot will be 1h long.
Smax = 16
deltaTslot = 1
start_hour = 6
end_hour = 22

# Nmax is the maximum number of charging stations available
Nmax = 3


# Before starting the algorithm for the day, we make sure that the sessions_of_the_day is a dict with the
# timeslot to start for every session and the connection and charging times
def get_sessions_with_starting_tslot(sessions_of_the_day):
    sessions_tslot = []
    for session in sessions_of_the_day:
        connection_time = pd.to_numeric(session['ConnectedTime'])
        charge_time = pd.to_numeric(session['ChargeTime'])

        session_start_hour = pd.to_datetime(session['Started']).hour
        session_start_timeslot = session_start_hour - start_hour + 1

        sessions_tslot.append({'timeslot': session_start_timeslot,
                               'time_to_depart': connection_time,
                               'time_to_full_charge': charge_time})
    return sessions_tslot


# BUG HERE (Find a way to remove properly)
def add_sessions_starting_in_this_tslot(timeslot, sessions_with_tslot, F):
    for session in sessions_with_tslot:
        if session['timeslot'] == timeslot:
            F.append(session)
    return F


# At the end of every iteration, the sessions with ConnectedTime == 0 must be erased because they are not connected
# anymore
def get_pruned_sessions(F):
    for session in F:
        if session['time_to_depart'] == 0:
            F.remove(session)
    return F


sessions_with_tslot = get_sessions_with_starting_tslot(sessions_of_the_day)
F = []

for timeslot in range(1, Smax):
    # This algorithm will be called every time that a new time slot starts, so it is supposed to receive a set F of Nmax
    # transactions every timeslot.
    F = add_sessions_starting_in_this_tslot(timeslot, sessions_with_tslot, F)

    # Initialize Xs with zeros
    Xs = np.zeros((Smax, Smax))


    # Ns is the number of EV currently connected
    Ns = len(F)

    for n in F:
        time_to_depart = n['time_to_depart']/deltaTslot
        time_to_full_charge = n['time_to_full_charge']/deltaTslot
        i = int(time_to_depart)
        j = int(time_to_full_charge)
        if time_to_depart <= 0:
            F.remove(n)
            Xs[j, i] -= 1
        else:
            Xs[j, i] += 1
            n['time_to_depart'] -= deltaTslot
            n['time_to_full_charge'] -= deltaTslot

    #F = get_pruned_sessions(F)

    print(Xs)

