tbsp
====

Transition-based semantic parser for Discourse Representation Structures.

Setup
-----

Make sure Git LFS is installed, then clone the repository and cd into the
working copy:

    git clone git@github.com:texttheater/tbsp.git
    cd tbsp

Download data from the [Parallel Meaning Bank](https://pmb.let.rug.nl):

    mkdir -p data
    cd data
    wget https://pmb.let.rug.nl/releases/exp_data_2.2.0.zip
    unzip exp_data_2.2.0.zip
    rm exp_data_2.2.0.zip
    mv exp_data_2.2.0 pmb-2.2.0
    wget https://pmb.let.rug.nl/releases/exp_data_3.0.0.zip
    unzip exp_data_3.0.0.zip
    rm exp_data_3.0.0.zip
    mv pmb_exp_data_3.0.0 pmb-3.0.0
    cd ..

Make sure the required Python packages are installed in your environment:

    pip3 install produce psutil pyyaml word2number Cython cmake torch h5py overrides nltk networkx
    pip3 install git+https://github.com/clab/dynet#egg=dynet

Clone/download required external software packages:

    mkdir -p ext
    git clone --branch v.2.2.0 https://github.com/RikVN/DRS_parsing.git ext/DRS_parsing
    git clone https://github.com/RikVN/DRS_parsing.git ext/DRS_parsing_3
    git clone https://github.com/HIT-SCIR/ELMoForManyLangs.git ext/ElMoForManyLangs
    git clone https://github.com/ParallelMeaningBank/elephant.git ext/elephant
    wget https://github.com/ufal/udpipe/releases/download/v1.2.0/udpipe-1.2.0-bin.zip
    unzip -d ext udpipe-1.2.0-bin.zip
    rm udpipe-1.2.0-bin.zip

Download ElMo models for English, German, Italian, and Dutch from
[ElMoForManyLangs](https://github.com/HIT-SCIR/ELMoForManyLangs):

    mkdir -p models/ElMoForManyLangs/{en,de,it,nl}
    wget http://vectors.nlpl.eu/repository/11/{142,144,159,164}.zip
    unzip -d models/ElMoForManyLangs/de 142.zip
    unzip -d models/ElMoForManyLangs/en 144.zip
    unzip -d models/ElMoForManyLangs/it 159.zip
    unzip -d models/ElMoForManyLangs/nl 164.zip
    sed -i 's~/Users/yijialiu/work/projects/conll2018/models/word_elmo/~../../../ext/ElMoForManyLangs/elmoformanylangs/configs/~' models/ElMoForManyLangs/en/config.json
    sed -i 's~/users4/conll18st/elmo/configs/~../../../ext/ElMoForManyLangs/configs/~' models/ElMoForManyLangs/elmoformanylangs/{de,it,nl}/config.json
    rm {142,144,159,164}.zip

Download [UDPipe models](http://ufal.mff.cuni.cz/udpipe/models) for lemmatization:

    wget --content-disposition -P models/udpipe "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/dutch-alpino-ud-2.5-191206.udpipe?sequence=20&isAllowed=y"
    wget --content-disposition -P models/udpipe "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/german-gsd-ud-2.5-191206.udpipe?sequence=32&isAllowed=y"
    wget --content-disposition -P models/udpipe "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/italian-isdt-ud-2.5-191206.udpipe?sequence=53&isAllowed=y"

Experiments
-----------

The results from Bladier et al. (2021) can be reproduced as follows.

First, run experiments on the PMB 3.0.0 development data:

    produce out/pmb-3.0.0.en.dev.gold.sg{0..5}g{1..20}.eval
    produce out/pmb-3.0.0.{de,it,nl}.dev.gold,s{0..20}.eval

Test the best-on-dev models on the test data:

    produce out/pmb-3.0.0.en.test.tok
    python3 decode.py en out/pmb-3.0.0.en.train.gold.oracles.jsonl out/pmb-3.0.0.en.train.sg4g16.model out/pmb-3.0.0.en.test.tok --mode 3 > test.clf
    python3 decode.py en out/pmb-3.0.0.en.train.gold.oracles.jsonl out/pmb-3.0.0.en.train.sg4g16.model out/pmb-3.0.0.en.test.tok --mode 3 test.clf -f2 data/pmb-3.0.0/en/gold/test.txt -prin -ill dummy -g ext/DRS_parsing_3/evaluation/clf_signature.yaml > test.eval

Now try with external SRL prediction, e.g., with CCG-based conversion and an
ELMo SRL model:

    python3 decode.py en out/pmb-3.0.0.en.train.gold.oracles.jsonl out/pmb-3.0.0.en.train.sg4g16.model out/pmb-3.0.0.en.test.tok --mode 3 --roles data/srl/drs_elmo.test.json --exp-key drs_elmo > test_drs_elmo.clf
    python3 decode.py en out/pmb-3.0.0.en.train.gold.oracles.jsonl out/pmb-3.0.0.en.train.sg4g16.model out/pmb-3.0.0.en.test.tok --mode 3 test_drs_elmo.clf -f2 data/pmb-3.0.0/en/gold/test.txt -prin -ill dummy -g ext/DRS_parsing_3/evaluation/clf_signature.yaml > test_drs_elmo.eval

References
----------

Tatiana Bladier, Gosse Minnema, Rik van Noord, Kilian Evang (2021): Improving
DRS Parsing with Separately Predicted Semantic Roles. Proceedings of CSTFRS.
