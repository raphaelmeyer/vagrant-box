import json
import os

class Config:
  def __init__(self, script_dir, config_file = "qtonpi.json"):
    self._config_file = config_file
    self.script_dir = script_dir
    self.build_dir = os.path.join(script_dir, 'build')
    self.patch_dir = os.path.join(script_dir, 'patches')
    self.vbox_dir = os.path.join(script_dir, 'vbox')
    self.patched_cd = os.path.join(self.build_dir, 'autoinstall.iso')
    self.install_cd_url = 'http://releases.ubuntu.com/13.04/ubuntu-13.04-server-i386.iso'
    self.patches = []
    self.vbox = {}
    self.vagrant_box = 'ubuntu-13.04-server-i386.box'
    self._parse()

  def _parse(self):
    data = ()
    with open(self._config_file, 'r') as config_file:
      data = json.load(config_file)

    if 'install_cd_url' in data:
      self.install_cd_url = data['install_cd_url']
    if 'patches' in data:
      self.patches = data['patches']
    if 'vbox' in data:
      self.vbox = data['vbox']
    if 'vagrant_box' in data:
      self.vagrant_box = data['vagrant_box']

