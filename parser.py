import dynet as dy
import elmo
import guess
import hyper
import numpy as np
import prep
import quantities
import rolesets
import sys
import times
import transit


class Parser:

    def __init__(self, lang, vocabulary, actions):
        self.lang = lang
        # inventories
        self.pc = dy.ParameterCollection()
        self.vocabulary = vocabulary
        self.actions = [('confirm',)]
        self.action_index_map = {('confirm',): 0}
        self.semtags = []
        self.semtag_index_map = {}
        self.rolesets = []
        self.roleset_index_map = {}
        for action in actions:
            if action[0] == 'confirm':
                semtag = action[1]
                if hyper.FACTOR_ROLESETS:
                    semtag, roleset = rolesets.extract(semtag)
                else:
                    roleset = ()
                if not semtag in self.semtag_index_map:
                    self.semtags.append(semtag)
                    self.semtag_index_map[semtag] = len(self.semtag_index_map)
                if not roleset in self.roleset_index_map:
                    self.rolesets.append(roleset)
                    self.roleset_index_map[roleset] = len(self.roleset_index_map)
            else:
                self.actions.append(action)
                self.action_index_map[action] = len(self.action_index_map)
        # print numbers
        print('{} actions'.format(len(self.actions)), file=sys.stderr)
        print('{} semtags'.format(len(self.semtags)), file=sys.stderr)
        print('{} rolelists'.format(len(self.rolesets)), file=sys.stderr)
        # RNNs
        self.buf_lstm = dy.LSTMBuilder(layers=hyper.LAYERS,
                                       input_dim=hyper.LSTM_INPUT_DIM,
                                       hidden_dim=hyper.HIDDEN_DIM,
                                       model=self.pc)
        self.stack_lstm = dy.LSTMBuilder(layers=hyper.LAYERS,
                                         input_dim=hyper.LSTM_INPUT_DIM,
                                         hidden_dim=hyper.HIDDEN_DIM,
                                         model=self.pc)
        self.actions_lstm = dy.LSTMBuilder(layers=hyper.LAYERS,
                                           input_dim=hyper.ACTION_DIM,
                                           hidden_dim=hyper.HIDDEN_DIM,
                                           model=self.pc)
        # EMBEDDINGS
        # learned word embeddings
        self.w = self.pc.add_lookup_parameters((len(vocabulary), hyper.INPUT_DIM))
        # pretrained word embeddings: no parameters, we use elmo.embed_sentence
        # input action embeddings
        self.a = self.pc.add_lookup_parameters((len(self.actions), hyper.ACTION_DIM))
        # relation embeddings (HACK: indices are shared with bind actions)
        self.r1 = self.pc.add_lookup_parameters((len(self.actions), hyper.REL_DIM))
        # mirror relation embeddings (HACK: indices are shared with bind actions)
        self.r2 = self.pc.add_lookup_parameters((len(self.actions), hyper.REL_DIM))
        # semtag embeddings
        self.n = self.pc.add_lookup_parameters((len(self.semtags), hyper.SEMTAG_DIM))
        # roleset embeddings
        self.o = self.pc.add_lookup_parameters((len(self.rolesets), hyper.ROLESET_DIM))
        # PARSER STATE
        # parser state bias
        self.pbias = self.pc.add_parameters(hyper.HIDDEN_DIM)
        # action lstm to parser state
        self.A = self.pc.add_parameters((hyper.HIDDEN_DIM, hyper.HIDDEN_DIM))
        # buffer lstm to parser state
        self.B = self.pc.add_parameters((hyper.HIDDEN_DIM, hyper.HIDDEN_DIM))
        # stack lstm to parser state
        self.S = self.pc.add_parameters((hyper.HIDDEN_DIM, hyper.HIDDEN_DIM))
        # LSTM
        # LSTM input bias
        self.ib = self.pc.add_parameters(hyper.LSTM_INPUT_DIM)
        # word to LSTM input
        self.w2l = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.INPUT_DIM))
        # pretrained word embeddings to LSTM input
        self.t2l = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.PRETRAINED_DIM))
        # INTERPRETATION FUNCTION
        # interpretation function bias
        self.nbias = self.pc.add_parameters(hyper.LSTM_INPUT_DIM)
        # semtag matrix for interpretation function
        self.N = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.SEMTAG_DIM))
        # roleset matrix for interpretation function
        self.O = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.ROLESET_DIM))
        # input matrix for interpretation function
        self.P = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.LSTM_INPUT_DIM))
        # LEFT-RIGHT COMPOSITION FUNCTION
        # left-right composition function bias
        self.cbias1 = self.pc.add_parameters(hyper.LSTM_INPUT_DIM)
        # left node matrix for left-right composition function
        self.H1 = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.LSTM_INPUT_DIM))
        # right node matrix for left-right composition function
        self.D1 = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.LSTM_INPUT_DIM))
        # binding relation matrix for left-right composition function
        self.R1 = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.REL_DIM))
        # RIGHT-LEFT COMPOSITION FUNCTION
        # right-left composition function bias
        self.cbias2 = self.pc.add_parameters(hyper.LSTM_INPUT_DIM)
        # right node matrix for right-left composition function
        self.H2 = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.LSTM_INPUT_DIM))
        # left node matrix for right-left composition function
        self.D2 = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.LSTM_INPUT_DIM))
        # binding relation matrix for right-left composition function
        self.R2 = self.pc.add_parameters((hyper.LSTM_INPUT_DIM, hyper.REL_DIM))
        # ADDITIONAL LAYER FOR ACTION CLASSIFIER
        self.pmodabias = self.pc.add_parameters(hyper.HIDDEN_DIM)
        self.pmoda = self.pc.add_parameters((hyper.HIDDEN_DIM, hyper.HIDDEN_DIM))
        # ACTION CLASSIFIER
        # action bias
        self.abias = self.pc.add_parameters(len(self.actions))
        # parser state to action
        self.p2a = self.pc.add_parameters((len(self.actions), hyper.HIDDEN_DIM))
        # ADDITIONAL LAYER FOR SEMTAG CLASSIFIER
        self.pmodsbias = self.pc.add_parameters(hyper.HIDDEN_DIM)
        self.pmods = self.pc.add_parameters((hyper.HIDDEN_DIM, hyper.HIDDEN_DIM))
        # SEMTAG CLASSIFIER
        # semtag bias
        self.sbias = self.pc.add_parameters(len(self.semtags))
        # parser state to semtag
        self.p2s = self.pc.add_parameters((len(self.semtags), hyper.HIDDEN_DIM))
        # ADDITIONAL LAYER FOR ROLESET CLASSIFIER
        self.pmodrbias = self.pc.add_parameters(hyper.HIDDEN_DIM)
        self.pmodr = self.pc.add_parameters((hyper.HIDDEN_DIM, hyper.HIDDEN_DIM))
        # ROLESET CLASSIFIER
        # roleset bias
        self.rbias = self.pc.add_parameters(len(self.rolesets))
        # parser state to roleset
        self.p2r = self.pc.add_parameters((len(self.rolesets), hyper.HIDDEN_DIM))
        # DUMMY SYMBOLS
        # dummy symbols signaling end of stack
        self.stack_guard = self.pc.add_parameters(hyper.LSTM_INPUT_DIM)
        self.action_start = self.pc.add_parameters(hyper.ACTION_DIM)
        self.buf_guard = self.pc.add_parameters(hyper.LSTM_INPUT_DIM)

    def save_model(self, path):
        self.pc.save(path)

    def load_model(self, path):
        self.pc.populate(path)

    def choose_action(self, p_t, allowed_action_indices):
        assert len(allowed_action_indices) > 0
        p_t = dy.tanh(dy.affine_transform([self.pmodabias, self.pmoda, p_t]))
        r_t = dy.affine_transform([self.abias, self.p2a, p_t])
        adiste = dy.log_softmax(r_t, allowed_action_indices)
        adist = adiste.vec_value()
        best_action_index = allowed_action_indices[0]
        best_score = adist[allowed_action_indices[0]]
        for i in range(1, len(allowed_action_indices)):
            action_index = allowed_action_indices[i]
            score = adist[action_index]
            if score > best_score:
                best_action_index = action_index
                best_score = score
        return adiste, best_action_index

    def choose_semtag(self, p_t):
        p_t = dy.tanh(dy.affine_transform([self.pmodsbias, self.pmods, p_t]))
        s_t = dy.affine_transform([self.sbias, self.p2s, p_t])
        sdiste = dy.log_softmax(s_t)
        sdist = sdiste.vec_value()
        best_semtag_index = np.argmax(sdist)
        return sdiste, best_semtag_index

    def choose_roleset(self, p_t, allowed_roleset_indices):
        p_t = dy.tanh(dy.affine_transform([self.pmodrbias, self.pmodr, p_t]))
        t_t = dy.affine_transform([self.rbias, self.p2r, p_t])
        rdiste = dy.log_softmax(t_t, allowed_roleset_indices)
        rdist = rdiste.vec_value()
        best_roleset_index = allowed_roleset_indices[0]
        best_score = rdist[allowed_roleset_indices[0]]
        for i in range(1, len(allowed_roleset_indices)):
            roleset_index = allowed_roleset_indices[i]
            score = rdist[roleset_index]
            if score > best_score:
                best_roleset_index = roleset_index
                best_score = score
        return rdiste, best_roleset_index

    def parse(self, sentence, lemmas=None, gold_actions=None):
        """Parse a sentence.
    
        If gold_actions is not None, runs in training mode and returns the loss
        (summed over all time steps). Otherwise, returns the predicted action
        sequence.
    
        sentence is a list of str tokens.
    
        gold_action_indices (if given) is a list of int action IDs.
        """
        # Prepare for training
        if gold_actions is not None:
            encoded_gold_actions = []
            for action in gold_actions:
                if action[0] == 'confirm':
                    semtag = action[1]
                    if hyper.FACTOR_ROLESETS:
                        semtag, roleset = rolesets.extract(semtag)
                    else:
                        roleset = ()
                    encoded_gold_actions.append((0,
                                                 self.semtag_index_map[semtag],
                                                 self.roleset_index_map[roleset]))
                else:
                    encoded_gold_actions.append((self.action_index_map[action],
                                                 None,
                                                 None))
            log_probs = []
        # Initialize buffer:
        sentence_rep = elmo.embed_sentence(sentence, lang=self.lang)
        buf = [(i, None, False) for i in reversed(range(len(sentence)))]
        buf_state = self.buf_lstm.initial_state()
        buf_state = buf_state.add_input(self.buf_guard)
        buf_inputs = []
        for i in range(len(sentence) - 1, -1, -1):
            token_rep = sentence_rep[i]
            w = dy.lookup(self.w, self.vocabulary.w2i(sentence[i]))
            t = dy.vecInput(hyper.PRETRAINED_DIM) # pretrained word embeddings (not updated)
            t.set(token_rep)
            inp = dy.rectify(dy.affine_transform([self.ib, self.w2l, w, self.t2l, t]))
            buf_inputs.append(inp)
            buf_state = buf_state.add_input(inp)
        # Initialize actions:
        actions = []
        actions_state = self.actions_lstm.initial_state()
        actions_state = actions_state.add_input(self.action_start)
        # Initialize stack:
        stack = []
        stack_state = self.stack_lstm.initial_state()
        stack_state = stack_state.add_input(self.stack_guard)
        stack_inputs = [] # keep stack LSTM stack_inputs, needed for interpretation/composition function
        # Initialize fragments:
        fragments = []
        # Parse:
        while len(stack) > 1 or len(buf) > 1:
            # compute parser state
            p_t = dy.rectify(dy.affine_transform([self.pbias,
                                                  self.S,
                                                  stack_state.h()[-1],
                                                  self.A,
                                                  actions_state.h()[-1],
                                                  self.B,
                                                  buf_state.h()[-1]]))
            # compute allowed actions
            allowed_action_indices = [i for i, a in enumerate(self.actions)
                if transit.is_action_allowed(a, stack, actions, buf)]
            # choose action based on parser state
            adist, action_index = self.choose_action(p_t, allowed_action_indices)
            if gold_actions is not None:
                gold_action_index, gold_semtag_index, gold_roleset_index = encoded_gold_actions[len(actions)]
                log_prob = dy.pick(adist, gold_action_index)
                log_probs.append(log_prob)
                action_index = gold_action_index
            action = self.actions[action_index]
            a = dy.lookup(self.a, action_index)
            actions_state = actions_state.add_input(a)
            if action[0] == 'confirm':
                # choose semtag based on parser state
                sdist, semtag_index = self.choose_semtag(p_t)
                if gold_actions is not None:
                    log_prob = dy.pick(sdist, gold_semtag_index)
                    log_probs.append(log_prob)
                    semtag_index = gold_semtag_index
                semtag = self.semtags[semtag_index]
                # choose roleset based on parser state
                if hyper.FACTOR_ROLESETS:
                    semtag, roleset = rolesets.extract(semtag)
                else:
                    roleset = ()
                allowed_roleset_indices = [i for i, r in enumerate(self.rolesets) if len(r) == len(roleset)]
                rdist, roleset_index = self.choose_roleset(p_t, allowed_roleset_indices)
                if gold_actions is not None:
                    log_prob = dy.pick(rdist, gold_roleset_index)
                    log_probs.append(log_prob)
                    roleset_index = gold_roleset_index
                roleset = self.rolesets[roleset_index]
                semtag = rolesets.insert(semtag, roleset)
                # guess names, strings, concepts
                word = sentence[stack[-1][0]]
                semtag = guess.guess_name(semtag, word)
                semtag = times.guess_times(semtag)
                semtag = quantities.guess_quantities(semtag)
                if lemmas:
                    lemma = lemmas[stack[-1][0]]
                    semtag = guess.guess_concept_from_lemma(semtag, lemma)
                else:
                    semtag = guess.guess_concept_from_word(semtag, word)
                action = ('confirm', semtag)
            else:
                semtag_index = None
                roleset_index = None
            transit.apply_action(action, stack, actions, buf, fragments)
            stack_state, actions_state, buf_state = self.apply_action(
                action_index, semtag_index, roleset_index, stack_state,
                stack_inputs, actions_state, buf_state, buf_inputs)
        # Return:
        if gold_actions is not None:
            return -dy.esum(log_probs)
        return actions, fragments

    def compose_lr(self, rel, left_inp, right_inp):
        rel_rep = dy.lookup(self.r1, rel)
        return dy.tanh(dy.affine_transform([self.cbias1, self.H1, left_inp,
            self.D1, right_inp, self.R1, rel_rep]))

    def compose_rl(self, rel, left_inp, right_inp):
        rel_rep = dy.lookup(self.r2, rel)
        return dy.tanh(dy.affine_transform([self.cbias2, self.H2, right_inp,
            self.D2, left_inp, self.R2, rel_rep]))

    def interpret(self, semtag_index, roleset_index, inp):
        semtag_rep = dy.lookup(self.n, semtag_index)
        roleset_rep = dy.lookup(self.o, roleset_index)
        return dy.tanh(dy.affine_transform([self.nbias,
                                            self.N, semtag_rep,
                                            self.O, roleset_rep,
                                            self.P, inp]))

    def apply_action(self, action_index, semtag_index, roleset_index,
        stack_state, stack_inputs, actions_state, buf_state, buf_inputs):
        action = self.actions[action_index]
        a = dy.lookup(self.a, action_index)
        actions_state = actions_state.add_input(a)
        if action[0] == 'confirm':
            stack_state = stack_state.prev()
            inp = stack_inputs.pop()
            inp = self.interpret(semtag_index, roleset_index, inp)
            stack_inputs.append(inp)
            stack_state = stack_state.add_input(inp)
        elif action[0] == 'reduce':
            stack_state = stack_state.prev()
            stack_inputs.pop()
        elif action[0] == 'bind':
            stack_state = stack_state.prev()
            stack_state = stack_state.prev()
            right_inp = stack_inputs.pop()
            left_inp = stack_inputs.pop()
            new_left_inp = self.compose_lr(action_index, left_inp, right_inp)
            new_right_inp = self.compose_rl(action_index, left_inp, right_inp)
            stack_inputs.append(new_left_inp)
            stack_inputs.append(new_right_inp)
            stack_state = stack_state.add_input(left_inp)
            stack_state = stack_state.add_input(right_inp)
        elif action[0] == 'swap':
            stack_state = stack_state.prev()
            stack_state = stack_state.prev()
            right_inp = stack_inputs.pop()
            left_inp = stack_inputs.pop()
            buf_inputs.append(left_inp)
            stack_inputs.append(right_inp)
            buf_state = buf_state.add_input(left_inp)
            stack_state = stack_state.add_input(right_inp)
        elif action[0] == 'shift':
            buf_state = buf_state.prev()
            inp = buf_inputs.pop()
            stack_inputs.append(inp)
            stack_state = stack_state.add_input(inp)
        else:
            raise Exception('unknown action type: ' + action[0])
        return stack_state, actions_state, buf_state
