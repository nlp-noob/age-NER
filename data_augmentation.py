from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from transformers import (
    HfArgumentParser,
)


@dataclass
class CustomArguments:
    window_size_after_augmentation: int = field(
        default=None,
        metadata={
            "help": (
                "In order to reduce the duplicated data ouside the augmentation data,"
                "The data is split into the window size for training beforehand."
            )
        },
    )
    input_data_path: str = field(
        default=None,
        metadata={
            "help": (
                "the input data path to be auged."
            )
        },
    )

    def __post_init__(self):
        if self.window_size_after_augmentation is None:
            raise ValueError("You should specify windowsize that the data is arranged after augmentation.")


def main():
    parser = HfArgumentParser((CustomArguments))
    custom_args = parser.parse_args_into_dataclasses()[0]
    import pdb;pdb.set_trace()


if __name__=="__main__":
    main()
