import torch

from typing import List, Tuple
from torch.nn.utils.rnn import pad_sequence


def pad_sequence_embeddings(batch: List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]
                            ) -> Tuple[List, torch.Tensor, torch.Tensor, None]:
    ids = [x[0] for x in batch]
    x = [x[1] for x in batch]
    y = [x[2] for x in batch]
    
    return ids, torch.stack(x), torch.stack(y), None


def pad_residue_embeddings(
        batch: List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]], padding_value=-100, batch_first=True
) -> Tuple[List, torch.Tensor, torch.Tensor, torch.LongTensor]:
    """

    :param batch_first: first dimension of return value will be batch
    :param padding_value: the value used for padding positions
    :param batch: An iteration batch from the ResidueEmbeddingsDataset class [(ID, emnbedding, label)]
    :return: Returns padded embeddings, labels, lengths and True/False mask for padding of input embeddings.
    """

    # Each element in "batch" is a tuple [(ID, embedding, label)]

    # Sort the batch in the descending order
    sorted_batch = sorted(batch, key=lambda x: x[1].shape[1], reverse=True)

    # Sequence ids:
    seq_ids = [x[0] for x in sorted_batch]

    # Get each residue-embedding and pad it
    sequences = [x[1] for x in sorted_batch]
    padded_sequences = pad_sequence(sequences, batch_first=batch_first, padding_value=0)

    # Also need to store the length of each sequence
    # This is later needed in order to unpad the sequences
    lengths = torch.LongTensor([len(x) for x in sequences])

    # Don't forget to grab the labels of the *sorted* batch
    padded_labels = pad_sequence([x[2] for x in sorted_batch], batch_first=batch_first, padding_value=padding_value)

    # Permute the embeddings to fit the LA architecture
    return seq_ids, padded_sequences, padded_labels, lengths
