import json
import glob
import random
import numpy as np
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense

from trajectory_helper import StateActionTuple
from session_helper import Nmax, Smax, get_possible_actions


def preprocess_trajectories(day_trajectories):
    F = []
    #i = 0
    for day in day_trajectories:
        state_actions = json.loads(open(day).read())['trajectories']
        state_action_tuples = [StateActionTuple(state_action) for state_action in state_actions]
        F.extend(state_action_tuples)
        #print(i)
        #i += 1
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


def train_function_approximator(x, y, n_epochs=10, batch_size=32):
    model = Sequential()
    model.add(Dense(128, input_dim=input_vector_size, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='linear'))

    model.compile(optimizer='rmsprop', loss=tf.losses.huber_loss)

    model.fit(x, y, epochs=n_epochs, batch_size=batch_size, verbose=2)

    return model


input_vector_size = Smax**2 + Smax + 1

# Train 75% - Test 25
#day_trajectories = sorted(glob.glob("/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/*.json"))
#day_trajectories = ["/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/trajectories_2018-10-31.json", "/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/trajectories_2018-10-30.json"]
train_day_trajectories = ["/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/trajectories_2018-10-31.json"]
#train_day_trajectories = random.sample(day_trajectories, int(len(day_trajectories) * 0.75))
#test_day_trajectories = list(set(day_trajectories) - set(train_day_trajectories))

train_F = preprocess_trajectories(train_day_trajectories)
#test_F = preprocess_trajectories(test_day_trajectories)

# Timeslot 1
state_action_tuples_timeslot_1 = [x for x in train_F if x.timeslot == 1]
print(len(state_action_tuples_timeslot_1))
x_Q1_T_reg, y_Q1_T_reg = split_T_reg(state_action_tuples_timeslot_1, None)
print('Length of T_reg = ' + str(len(x_Q1_T_reg)))

Q1_approximated_function = train_function_approximator(x_Q1_T_reg, y_Q1_T_reg)


# Timeslot 2
state_action_tuples_timeslot_2 = [x for x in train_F if x.timeslot == 2]
print(len(state_action_tuples_timeslot_2))
x_Q2_T_reg, y_Q2_T_reg = split_T_reg(state_action_tuples_timeslot_2, Q1_approximated_function)
print('Length of T_reg = ' + str(len(x_Q2_T_reg)))

Q2_approximated_function = train_function_approximator(x_Q2_T_reg, y_Q2_T_reg)


# Timeslot 3
state_action_tuples_timeslot_3 = [x for x in train_F if x.timeslot == 3]
#print(len(state_action_tuples_timeslot_3))
#x_Q3_T_reg, y_Q3_T_reg = split_T_reg(state_action_tuples_timeslot_3, None)
s_a_tuple = state_action_tuples_timeslot_3[0]
predict_me_sth = np.array(np.array([s_a_tuple.timeslot, *s_a_tuple.Xs.flatten(), *s_a_tuple.us]))
result = Q2_approximated_function.predict(np.reshape(predict_me_sth, (1, len(predict_me_sth))))
print(result)
