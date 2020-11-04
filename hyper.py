UNK_PROB = 0.2


# Architecture from https://github.com/clab/lstm-parser/blob/master/parser/lstm-parse.cc
# TODO find more suitable hyperparameters
LAYERS = 2
INPUT_DIM = 40
HIDDEN_DIM = 100
ACTION_DIM = 20
PRETRAINED_DIM = 1024 # average of 3 ELMo layers
LSTM_INPUT_DIM = 100
REL_DIM = 20
SEMTAG_DIM = 20
ROLESET_DIM = 20


BATCH_SIZE = 1
ETA = 0.1
ETA_DECAY = 0.08


FACTOR_ROLESETS = True
