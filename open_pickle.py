import pickle 
with open('inverted_index.pickle', 'rb') as handle:
    b = pickle.load(handle)
    print(b['flask'])