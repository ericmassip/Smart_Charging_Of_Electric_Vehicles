import glob
import os
import pickle
import click

from session_helper import Smax
from fqi_helper import *


@click.command()
@click.option(
    '--n_epochs',
    type=click.INT,
    required=True,
    help='Number of epochs for the training of the neural network.'
)
@click.option(
    '--batch_size',
    type=click.INT,
    required=True,
    help='Batch size for the training of the neural network.'
)
@click.option(
    '--samples',
    type=click.STRING,
    required=True,
    help="This parameter refers to the 'top sampling trajectories' used in the extraction of the trajectories."
)
@click.option(
    '--trajectories_path',
    type=click.STRING,
    required=True,
    help='Path to the file where the trajectories are saved.'
)
@click.option(
    '--models_directory',
    type=click.STRING,
    required=True,
    help='Path to the directory where the models will be saved.'
)
@click.option(
    '--baseline/--pv',
    required=True,
    help='Whether you want to train the Baseline network without PV data as input or the PV network with PV data.'
)
def train_fqi(n_epochs, batch_size, samples, trajectories_path, models_directory, baseline):

    if baseline:
        input_vector_size = Smax ** 2 + Smax + 1
        network = 'Baseline'
    else:
        input_vector_size = Smax ** 2 + Smax + 1 + 1
        network = 'PV'

    day_trajectories = sorted(glob.glob(trajectories_path + str(samples) + "/*.json"))
    #day_trajectories = ["/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/5000/trajectories_2018-10-31.json", "/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/5000/trajectories_2018-10-30.json"]
    #day_trajectories = ["/Users/ericmassip/Projects/MAI/Thesis/datasets/Trajectories/5000/trajectories_2018-10-31.json"]
    #day_trajectories = [trajectories_path + str(samples) + "/trajectories_2018-10-31.json"]

    train_day_trajectories = []
    for i in range(len(day_trajectories)):
        if i == 0 or i % 5 != 0:
            train_day_trajectories.append(day_trajectories[i])

    train_F = preprocess_trajectories(train_day_trajectories)
    #pickle.dump(train_F, open('train_F_' + samples + '.p', 'wb'))

    #train_F = pickle.load(open('train_F_' + samples + '.p', mode='rb'))

    print('There are ' + str(len(train_day_trajectories)) + ' training days.')

    models_directory = models_directory + network + '/samples_' + str(samples) + '_n_epochs_' + str(n_epochs) + '_batch_size_' + str(batch_size) + '/'
    if not os.path.exists(models_directory):
        os.makedirs(models_directory)

    previous_Q_approximated_function = None
    # Training
    for timeslot in range(Smax, 0, -1):
        print('')
        print('')
        print('Iteration for timeslot ' + str(timeslot))

        state_action_tuples = [x for x in train_F if x.timeslot == timeslot]

        x_T_reg, y_T_reg = split_T_reg_for_FQI_Reverse(timeslot, state_action_tuples, previous_Q_approximated_function, network)

        model = train_function_approximator(x_T_reg, y_T_reg, n_epochs, batch_size, input_vector_size)
        model.save(models_directory + 'Q' + str(timeslot) + '_approximated_function.h5')
        previous_Q_approximated_function = model


if __name__ == '__main__':
    train_fqi()