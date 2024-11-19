import json
import os.path


class Config:
    def __init__(self, config_file):
        self.__config_file = config_file
        if not os.path.exists(self.__config_file):
            open(self.__config_file, "w+").close()
        with open(self.__config_file, "r+") as f:
            config_string = f.read()
        if config_string == "":
            config_string = "{}"
        self._config = json.loads(config_string)

    def _get_property(self, property_name, default_value=None):
        try:
            if property_name not in self._config.keys():
                return default_value
            return self._config[property_name]
        except json.decoder.JSONDecodeError:
            # clear config on error
            os.remove(self.__config_file)
            self._config = "{}"

    def _set_property(self, property_name, value):
        self._config[property_name] = value

    def save_config(self):
        with open(self.__config_file, "w+") as f:
            print("Save:", self._config)
            f.write(json.dumps(self._config))


class CameraConfig(Config):
    def __init__(self):
        super().__init__("camera_config.json")

    @property
    def camera_name(self):
        return self._get_property('camera_name', 0)

    @camera_name.setter
    def camera_name(self, name):
        self._set_property("camera_name", name)

    @property
    def projector_edges(self):
        return self._get_property('projector_edges')

    @projector_edges.setter
    def projector_edges(self, name):
        self._set_property("projector_edges", name)
