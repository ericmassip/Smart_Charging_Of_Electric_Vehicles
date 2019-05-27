import json
import numpy as np
import tensorflow as tf
import pickle

from keras.models import Sequential
from keras.layers import Dense

import keras.losses
keras.losses.huber_loss = tf.losses.huber_loss

from trajectory_helper import StateActionTuple, get_unique_state_action_tuples
from session_helper import Nmax, get_possible_actions


def preprocess_trajectories(day_trajectories):
    F = []
    counter = 0
    for day in day_trajectories:
        state_actions = json.loads(open(day).read())['trajectories']
        state_action_tuples = [StateActionTuple(state_action) for state_action in state_actions]

        #for elem in state_action_tuples:
        #    if elem not in F:
        #        F.extend(state_action_tuples)

        if not F:
            F = get_unique_state_action_tuples(state_action_tuples)
        else:
            unique_state_action_tuples_to_be_added = get_unique_state_action_tuples(state_action_tuples)
            for i in range(len(unique_state_action_tuples_to_be_added)):
                elem = unique_state_action_tuples_to_be_added[i]
                found = False
                j = 0
                while not found and j < len(F):
                    elem2 = F[j]

                    if i != j and elem.is_equal(elem2):
                        found = True

                    j += 1

                if not found:
                    F.append(elem)

        if counter % 5 == 0:
            print('Preprocessed ' + str(counter + 1) + ' days.')
        counter += 1

    #pickle.dump(F, open('F_with_uniques.p', 'wb'))
    return F


def split_T_reg_for_FQI(iteration, F, previous_Q_approximated_function, network):
    x = []
    y = []

    for i in range(len(F)):
        s_a_tuple = F[i]
        q_value_of_current_state = s_a_tuple.cost

        if iteration != 1:
            q_value_of_current_state += calculate_q_value(s_a_tuple, previous_Q_approximated_function, network)

        if network == 'Baseline':
            x.append([s_a_tuple.timeslot, *s_a_tuple.Xs.flatten(), *s_a_tuple.us])
        elif network == 'PV':
            x.append([s_a_tuple.timeslot, s_a_tuple.pv, *s_a_tuple.Xs.flatten(), *s_a_tuple.us])
        else:
            print('ERROR: No network set -> ' + network)

        y.append(q_value_of_current_state)

        if i % 10000 == 0:
            print(i)

    return np.array(x), np.array(y)


def split_T_reg_for_FQI_Reverse(timeslot, F, previous_Q_approximated_function, network):
    x = []
    y = []

    for i in range(len(F)):
        s_a_tuple = F[i]
        q_value_of_current_state = s_a_tuple.cost

        if timeslot != 8:
            q_value_of_current_state += calculate_q_value(s_a_tuple, previous_Q_approximated_function, network)

        if network == 'Baseline':
            x.append([s_a_tuple.timeslot, *s_a_tuple.Xs.flatten(), *s_a_tuple.us])
        elif network == 'PV':
            x.append([s_a_tuple.timeslot, s_a_tuple.pv, *s_a_tuple.Xs.flatten(), *s_a_tuple.us])
        else:
            print('ERROR: No network set -> ' + network)

        y.append(q_value_of_current_state)

        if i % 10000 == 0:
            print(i)

    return np.array(x), np.array(y)


def calculate_q_value(s_a_tuple, previous_Q_approximated_function, network):
    possible_actions_next_state = get_possible_actions(Nmax * s_a_tuple.resulting_Xs)
    possible_q_values_next_state = [predict(s_a_tuple, action, previous_Q_approximated_function, network) for action in possible_actions_next_state]
    minimum_q_value_next_state = min(possible_q_values_next_state)
    return minimum_q_value_next_state[0][0]


def predict(s_a_tuple, action, previous_Q_approximated_function, network):
    if network == 'Baseline':
        predict_me_sth = np.array([s_a_tuple.next_timeslot, *s_a_tuple.resulting_Xs.flatten(), *action])
        return previous_Q_approximated_function.predict(np.reshape(predict_me_sth, (1, len(predict_me_sth))))

    elif network == 'PV':
        predict_me_sth = np.array([s_a_tuple.next_timeslot, s_a_tuple.next_pv, *s_a_tuple.resulting_Xs.flatten(), *action])
        return previous_Q_approximated_function.predict(np.reshape(predict_me_sth, (1, len(predict_me_sth))))

    else:
        print('ERROR: No network set -> ' + network)


def train_function_approximator(x, y, n_epochs, batch_size, input_vector_size):
    model = Sequential()
    model.add(Dense(128, input_dim=input_vector_size, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='linear'))

    model.compile(optimizer='rmsprop', loss=tf.losses.huber_loss)

    model.fit(x, y, epochs=n_epochs, batch_size=batch_size, validation_split=0.2, verbose=2)

    return model