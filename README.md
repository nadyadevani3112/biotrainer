# Biotrainer

*Biotrainer* is an open-source tool to simplify the training process of machine-learning models for biological
applications. It specializes on models to predict features for **proteins**. *Biotrainer* supports both, **training**
new models and employing the trained model for **inference**.
Using *biotrainer* comes as simple as providing your sequence and label data in the 
[correct format](#data-standardization), along with a [configuration file](#example-configuration-file).

## Installation

1. Make sure you have [poetry](https://python-poetry.org/) installed: 
```bash
curl -sSL https://install.python-poetry.org/ | python3 -
```

2. Install dependencies and biotrainer via `poetry`:
```bash
# In the base directory:
poetry install
# Adding jupyter notebook (if needed):
poetry add jupyter

# [WINDOWS] Explicitly install torch libraries suited for your hardware:
# Select hardware and get install command here: https://pytorch.org/get-started/locally/
# Then run for example:
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
**Please make sure to use the same torch version as provided in `pyproject.toml` for model reproducibility!**

## Training

```bash
cd examples/residue_to_class
poetry run biotrainer config.yml
```

You can also use the provided `run-biotrainer.py` file for development and debugging (you might want to set up your 
IDE to directly execute run-biotrainer.py with the provided virtual environment):
```bash
# residue_to_class
poetry run python3 run-biotrainer.py examples/residue_to_class/config.yml
# sequence_to_class
poetry run python3 run-biotrainer.py examples/sequence_to_class/config.yml
```

### Training in Docker

```bash
# Build
docker build -t biotrainer .
# Run
docker run --rm \
    -v "$(pwd)/examples/docker":/mnt \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    biotrainer:latest /mnt/config.yml
```

Output can be found afterward in the directory of the provided configuration file.

## Inference

After your model is trained, you will find an `out.yml` file in the `output` directory by default. Now you can use
that to create predictions with your model for new data, the `inferencer` module takes care of loading your checkpoints
automatically:
```python
from biotrainer.inference import Inferencer
from biotrainer.embedders import OneHotEncodingEmbedder

sequences = [
    "PROVTEIN",
    "SEQVENCESEQVENCE"
]

out_file_path = '../residue_to_class/output/out.yml'

inferencer, out_file = Inferencer.create_from_out_file(out_file_path=out_file_path, allow_torch_pt_loading=True)

print(f"For the {out_file['model_choice']}, the metrics on the test set are:")
for metric in out_file['test_iterations_results']['metrics']:
    print(f"\t{metric} : {out_file['test_iterations_results']['metrics'][metric]}")


embedder = OneHotEncodingEmbedder()
embeddings = list(embedder.embed_many(sequences))
# Note that for per-sequence embeddings, you would have to reduce the embeddings now:
# embeddings = [[embedder.reduce_per_protein(embedding)] for embedding in embeddings]
predictions = inferencer.from_embeddings(embeddings, split_name="hold_out")
for sequence, prediction in zip(sequences, predictions["mapped_predictions"].values()):
    print(sequence)
    print(prediction)

# If your checkpoints are stored as .pt, consider converting them to safetensors (supported by biotrainer >=0.9.1)
inferencer.convert_all_checkpoints_to_safetensors()
```
See the full example [here](examples/inference/predict.py).

The `inferencer` module also features predicting with `bootstrapping` and `monte carlo dropout`. 

## Data standardization

*Biotrainer* provides a lot of data standards, designed to ease the usage of machine learning for biology. 
This standardization process is also expected to improve communication between different scientific disciplines
and help to keep the overview about the rapidly developing field of protein prediction.

### Available protocols

The protocol defines, how the input data should be interpreted and which kind of prediction task has to be applied.
The following protocols are already implemented:
```text
D=embedding dimension (e.g. 1024)
B=batch dimension (e.g. 30)
L=sequence dimension (e.g. 350)
C=number of classes (e.g. 13)

- residue_to_class --> Predict a class C for each residue encoded in D dimensions in a sequence of length L. Input BxLxD --> output BxLxC
- residues_to_class --> Predict a class C for all residues encoded in D dimensions in a sequence of length L. Input BxLxD --> output BxC
- residues_to_value --> Predict a value V for all residues encoded in D dimensions in a sequence of length L. Input BxLxD --> output Bx1
- sequence_to_class --> Predict a class C for each sequence encoded in a fixed dimension D. Input BxD --> output BxC
- sequence_to_value --> Predict a value V for each sequence encoded in a fixed dimension D. Input BxD --> output Bx1
```

### Input file standardization

For every protocol, we created a standardization on how the input data must be provided. You can find detailed 
information for each protocol [here](docs/data_standardization.md).

Below, we show an example on how the sequence and label file must look like for the *residue_to_class* protocol:

**sequences.fasta**
```fasta
>Seq1
SEQWENCE
```

**labels.fasta**
```fasta
>Seq1 SET=train VALIDATION=False
DVCDVVDD
```

### Configuration file

To run *biotrainer*, you need to provide a configuration file in `.yaml` format along with your sequence and label data. 
Here you can find an exemplary file for the *residue_to_class* protocol. All configuration options are listed
[here](docs/config_file_options.md).

**Example configuration for residue_to_class**:
```yaml
protocol: residue_to_class
sequence_file: sequences.fasta # Specify your sequence file
labels_file: labels.fasta # Specify your label file
model_choice: CNN # Model architecture 
optimizer_choice: adam # Model optimizer
learning_rate: 1e-3 # Optimizer learning rate
loss_choice: cross_entropy_loss # Loss function 
use_class_weights: True # Balance class weights by using class sample size in the given dataset
num_epochs: 200 # Number of maximum epochs
batch_size: 128 # Batch size
embedder_name: Rostlab/prot_t5_xl_uniref50 # Embedder to use
```

### (Bio-)Embeddings

To convert the sequence data to more meaningful input for a model, embeddings generated by 
*protein language models* (pLMs) have become widely applied in the last years. 
Hence, *biotrainer* enables automatic calculation of embeddings on a *per-sequence* and *per-residue* level, 
depending on the protocol. 
Take a look at the [embeddings options](docs/config_file_options.md#embeddings) to find out about all the available
embedding methods. It is also possible to provide your own embeddings file using your own embedder, 
independent of the provided calculation pipeline. Please refer to the 
[data standardization](docs/data_standardization.md#embeddings) document and the 
[relevant examples](examples/custom_embeddings/) to learn how to do this. Pre-calculated embeddings can be used for
the training process via the `embeddings_file` parameter, 
as described in the [configuration options](docs/config_file_options.md#embeddings).

## Troubleshooting

If you are experiencing any problems during installation or running, 
please check the [Troubleshooting Guide](docs/troubleshooting.md) first.

If your problem is not covered there, please [create an issue](https://github.com/sacdallago/biotrainer/issues/new).

## Citation

If you are using *biotrainer* for your work, please add a citation:

```text
@inproceedings{
sanchez2022standards,
title={Standards, tooling and benchmarks to probe representation learning on proteins},
author={Joaquin Gomez Sanchez and Sebastian Franz and Michael Heinzinger and Burkhard Rost and Christian Dallago},
booktitle={NeurIPS 2022 Workshop on Learning Meaningful Representations of Life},
year={2022},
url={https://openreview.net/forum?id=adODyN-eeJ8}
}
```
