""" Creates the test.pickle file to make a mock index for testing. """
import pickle

def create_test_pickle():
    """ One time use function to create the test pickle.
    fake_index is the content of the pickle.
    """

    fake_index = {
        'hello' : { 1, 2, 3},
        'bye' : { 2, 3 },
        'good' : { 4, 5 },
        'bad' : { 1 }
    }

    with open('test.pickle', 'wb') as handle:
        pickle.dump(fake_index, handle, protocol=pickle.HIGHEST_PROTOCOL)

create_test_pickle()
