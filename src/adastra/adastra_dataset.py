from src.common.dataset import Dataset

from src.adastra.util import base_utils
from src.adastra.util import nlp_utils


class AdastraDataset(Dataset):
    """
    
    """
    def __init__(
        self,

        name,
        file,
        adastra_dir,
        main_character,
        use_nlp = False,
    ):
        self.name = name
        self.file = file
        self.adastra_dir = adastra_dir
        self.main_character = main_character
        self.use_nlp = use_nlp

        self.result = None


    def build_dataset(self, datasets=None):
        print(f"\nBuilding Adastra dataset using script files in `{self.adastra_dir}`...")
        adastra_dataset = base_utils.build_adastra_data(
            adastra_directory=self.adastra_dir,
            main_character=self.main_character
        )
        print("@ Adastra dataset complete!")

        # Apply optional NLP processing if specified.
        if self.use_nlp:
            print(
                "@ Augmenting dataset with NLP... (This process takes about a minute.)"
            )
            adastra_dataset = nlp_utils.nlp_augment_adastra_data(adastra_dataset)
            print("@ Dataset augmented!")

        self.result = adastra_dataset
        return adastra_dataset
