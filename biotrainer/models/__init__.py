import inspect

from .CNN import CNN
from .LogReg import LogReg
from .FNN import FNN, DeeperFNN
from .LightAttention import LightAttention
from .model_params import count_parameters

__MODELS = {
    'residue_to_class': {
        'CNN': CNN,
        'FNN': FNN,
        'DeeperFNN': DeeperFNN,
        'LogReg': LogReg,
    },
    'residues_to_class': {
        'LightAttention': LightAttention,
    },
    'sequence_to_class': {
        'FNN': FNN,
        'DeeperFNN': DeeperFNN,
        'LogReg': LogReg
    },
    'sequence_to_value': {
        'FNN': FNN,
        'DeeperFNN': DeeperFNN,
        'LogReg': LogReg
    },
}


def get_model(protocol: str, model_choice: str, n_classes: int, n_features: int,
              **kwargs):
    model = __MODELS.get(protocol).get(model_choice)

    if not model:
        raise NotImplementedError
    else:
        if "dropout_rate" in kwargs.keys() and "dropout_rate" not in inspect.signature(model).parameters:
            raise NotImplementedError(f"dropout_rate not implemented for model_choice {model_choice}")

        return model(n_classes=n_classes, n_features=n_features, **kwargs)


def get_all_available_models():
    return dict(__MODELS)


__all__ = [
    "get_model",
    "get_all_available_models",
    "count_parameters",
]
