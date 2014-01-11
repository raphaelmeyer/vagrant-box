from config import Config
from install_cd import InstallCD
from vbox_image import VBoxImage

class Image:
  def __init__(self, script_dir, config_file = 'config.json'):
    self._config_file = config_file
    self._script_dir = script_dir

  def create(self):
    config = Config(self._script_dir, self._config_file)

    install_cd = InstallCD(config)
    install_cd.create()

    image = VBoxImage(config)
    image.setup()
    image.package()

