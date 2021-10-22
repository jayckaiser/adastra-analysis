import sys
import yaml


class Configs(dict):
    """
    Custom dictionary implementation to add `check_keys` and return Configs in iteration.
    """
    def __init__(self, dict_):
        super().__init__(dict_)

    
    @classmethod
    def load_yaml(cls, filepath):
        """
        Standardized method to load a YAML file and instantiate a Configs.
        """
        with open(filepath, 'r') as fp:
            return Configs(
                yaml.load(fp, Loader=yaml.FullLoader)
            )

    
    def get(self, k, default=None):
        """
        Custom instantiation of .get().
        If a dict is retrieved, wrap in Configs.
        If a list of dicts, wrap all in Configs.
        """
        _value = super().get(k)

        if _value is None:
            return default

        if isinstance(_value, dict):
            _dict = {
                k: Configs(v) if isinstance(v, dict) else v
                for k, v in _value.items()
            }
            return Configs(_dict)
        elif isinstance(_value, list):
            return [
                Configs(x) if isinstance(x, dict) else x
                for x in _value
            ]
        else:
            return _value

    
    def check_keys(self, keys):
        """
        Verify that all required dict keys are present to run a script.
        Raises an error prematurely to prevent unnecessary processing.
        """
        success = True

        for key in keys:
            if key not in self:
                print(
                    f"Config key `{key}` is required to run this script!"
                )
                success = False

        if not success:
            print("Please fix missing keys and try again!")
            sys.exit(0)

    