import os


class Run:
    """
    
    """
    def __init__(
        self,

        name,
        file,
        dataset,
    ):
        self.name = name
        self.file = file
        self.dataset = dataset

        self.result = None


    @classmethod
    def yaml_constructor(cls, loader, node):
        return cls(**loader.construct_mapping(node, deep=True))


    @staticmethod
    def prepare_directories(file):
        """
        Create missing directories and notify the user.
        """
        directory = os.path.dirname(file)

        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"@ Created new directory: `{directory}`")