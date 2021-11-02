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


    def build(self, datasets=None):
        pass

    def save(self):
        pass

    def run(self, datasets):
        result = self.build(datasets)
        self.save(result)


    @classmethod
    def yaml_constructor(cls, loader, node):
        """
        Each subclass should have a YAML initiator.
        """
        return cls(**loader.construct_mapping(node, deep=True))


    @staticmethod
    def prepare_directories(file):
        """
        Create missing directories and notify the user.
        This is used in all write steps.
        """
        directory = os.path.dirname(file)

        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"@ Created new directory: `{directory}`")