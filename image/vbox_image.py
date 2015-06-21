# V[irtual]Box
# V[agrant]Box

import subprocess
import shlex
import os

from image.virtualbox import VirtualBox

class VBoxImage:
  def __init__(self, config):
    self._config = config

  def _install_ssh_key(self, ssh_port):
    ssh_public_key = os.path.join(self._config.script_dir, 'resources/vagrant.pub')
    proc = subprocess.Popen(shlex.split('sshpass -p vagrant ssh-copy-id -i "{0}" -p {1} -o StrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null vagrant@localhost'.format(ssh_public_key, ssh_port)), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode is not 0:
      raise Exception(str(out) + '\n' + str(err))


  def setup(self):
    print("Create virtual machine")
    vbox = VirtualBox(self._config.vbox['name'], self._config.vbox_dir)
    vbox.createvm(self._config.vbox)

    print("Install base image")
    vbox.insert_cd(self._config.patched_cd)
    vbox.startvm()
    vbox.wait_for_shutdown()
    vbox.remove_cd()

    print("Install ssh key")
    ssh_port = 2222
    vbox.forward_ssh(ssh_port)
    vbox.startvm()
    vbox.wait_for_started()
    self._install_ssh_key(ssh_port)
    vbox.stopvm()
    vbox.wait_for_shutdown()

  def package(self):
    print("Package vagrant box")
    vbox_name = self._config.vbox['name']
    vagrant_box = os.path.join(self._config.script_dir, self._config.vagrant_box)
    proc = subprocess.Popen(shlex.split('vagrant package --base "{0}" --output "{1}"'.format(vbox_name, vagrant_box)), stdout=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode is not 0:
      raise Exception(str(err))

