tbsp
====

Transition-based semantic parser for Discourse Representation Structures.

Setup
-----

Make sure Git LFS is installed, then clone the repository and cd into the
working copy:

    git lfs init
    git clone git@github.com:texttheater/tbsp.git
    cd tbsp

Download data from the [Parallel Meaning Bank](https://pmb.let.rug.nl):

    mkdir -p data
    wget https://pmb.let.rug.nl/releases/pmb-2.2.0.zip
    unzip -d data pmb-2.2.0.zip
    rm pmb-2.2.0.zip

Run the data extraction script:

    cd data/pmb-2.2.0
    bash src/extract.sh
    cd ../..

Make sure the required Python packages are installed in your environment:

    pip3 install produce psutil pyyaml word2number Cython cmake torch h5py overrides nltk networkx
    pip3 install git+https://github.com/clab/dynet#egg=dynet

Clone/download required external software packages:

    mkdir -p ext
    git clone --branch v.2.2.0 https://github.com/RikVN/DRS_parsing.git ext/DRS_parsing # for postprocessing and evaluation; note that newer versions are not supported yet
    git clone https://github.com/HIT-SCIR/ELMoForManyLangs.git ext/ElMoForManyLangs
    git clone https://github.com/ParallelMeaningBank/elephant.git ext/elephant # for tokenization
    wget https://github.com/ufal/udpipe/releases/download/v1.2.0/udpipe-1.2.0-bin.zip # for lemmatization
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

Run experiments on the PMB 2.2.0 development data:

    produce out/pmb-2.2.0.en.dev.gold.sg{0..20}g{1..20}.eval
    produce out/pmb-2.2.0.{de,it,nl}.dev.gold,s{0..20}.eval

Test the best-on-dev models on the test data:

TBC
