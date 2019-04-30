import json
import glob
import numpy as np
import tensorflow as tf
import os
import pickle

from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model

import keras.losses
keras.losses.huber_loss = tf.losses.huber_loss

from trajectory_helper import StateActionTuple
from session_helper import Nmax, Smax, get_possible_actions


def preprocess_trajectories(day_trajectories):
    F = []
    i = 0
    for day in day_trajectories:
        state_actions = json.loads(open(day).read())['trajectories']
        state_action_tuples = [StateActionTuple(state_action) for state_action in state_actions]
        F.extend(state_action_tuples)
        if i % 5 == 0:
            print('Preprocessed ' + str(i + 1) + ' days.')
        i += 1
    return F


def split_T_reg(F, previous_Q_approximated_function):
    x = []
    y = []
    for s_a_tuple in F:
        q_value_of_current_state = s_a_tuple.cost

        if s_a_tuple.timeslot != 1:
            q_value_of_current_state += calculate_q_value(s_a_tuple, previous_Q_approximated_function)

        x.append([s_a_tuple.timeslot, *s_a_tuple.Xs.flatten(), *s_a_tuple.us])
        y.append(q_value_of_current_state)

    return np.array(x), np.array(y)


def calculate_q_value(s_a_tuple, previous_Q_approximated_function):
    possible_actions_next_state = get_possible_actions(Nmax * s_a_tuple.resulting_Xs)
    possible_q_values_next_state = [predict(s_a_tuple, action, previous_Q_approximated_function) for action in possible_actions_next_state]
    minimum_q_value_next_state = min(possible_q_values_next_state)
    return minimum_q_value_next_state[0][0]


def predict(s_a_tuple, action, previous_Q_approximated_function):
    predict_me_sth = np.array([s_a_tuple.next_timeslot, *s_a_tuple.resulting_Xs.flatten(), *action])
    return previous_Q_approximated_function.predict(np.reshape(predict_me_sth, (1, len(predict_me_sth))))


def train_function_approximator(x, y, n_epochs, batch_size, loss):
    model = Sequential()
    model.add(Dense(128, input_dim=input_vector_size, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='linear'))

    #model.compile(optimizer='rmsprop', loss=loss)
    model.compile(optimizer='rmsprop', loss=tf.losses.huber_loss)

    model.fit(x, y, epochs=n_epochs, batch_size=batch_size, validation_split=0.2, verbose=2)

    return model


input_vector_size = Smax**2 + Smax + 1

n_epochs = 1
batch_size = 256
loss = 'huber'
samples = 5000
network = 'PV' # 'Baseline' or 'PV'

day_trajectories = sorted(glob.glob("/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/" + network + "/" + str(samples) + "/*.json"))
#day_trajectories = ["/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/5000/trajectories_2018-10-31.json", "/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/5000/trajectories_2018-10-30.json"]
#day_trajectories = ["/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/all/trajectories_2018-10-31.json", "/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/all/trajectories_2018-10-30.json"]
#day_trajectories = ["/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/Baseline/all/trajectories_2018-10-31.json"]

train_day_trajectories = []
for i in range(len(day_trajectories)):
    if i == 0 or i % 5 != 0:
        train_day_trajectories.append(day_trajectories[i])

train_F = preprocess_trajectories(train_day_trajectories)
pickle.dump(train_F, open('train_F.p', 'wb'))

#train_F = pickle.load(open('train_F.p', mode='rb'))

print('There are ' + str(len(train_day_trajectories)) + ' training days.')

models_directory = '../../../models/network_' + str(network) + '_samples_' + str(samples) + '_n_epochs_' + str(n_epochs) + '_batch_size_' + str(batch_size) + '_loss_' + loss + '/'
if not os.path.exists(models_directory):
    os.makedirs(models_directory)

previous_Q_approximated_function = None
# Training
for timeslot in range(1, Smax + 1):
    print('')
    print('')
    print('Iteration for timeslot ' + str(timeslot))

    state_action_tuples = [x for x in train_F if x.timeslot == timeslot]
    x_T_reg, y_T_reg = split_T_reg(state_action_tuples, previous_Q_approximated_function)

    model = train_function_approximator(x_T_reg, y_T_reg, n_epochs, batch_size, loss)
    model.save(models_directory + 'Q' + str(timeslot) + '_approximated_function.h5')
    previous_Q_approximated_function = model


#Do the saved models predict sth?
for timeslot in range(1, Smax + 1):
    state_action_tuples = [x for x in train_F if x.timeslot == timeslot]
    s_a_tuple = state_action_tuples[0]
    predict_me_sth = np.array(np.array([s_a_tuple.timeslot, *s_a_tuple.Xs.flatten(), *s_a_tuple.us]))

    model = load_model(models_directory + 'Q' + str(timeslot) + '_approximated_function.h5')
    result = model.predict(np.reshape(predict_me_sth, (1, len(predict_me_sth))))
    print(result)
