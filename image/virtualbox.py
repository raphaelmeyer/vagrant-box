import subprocess
import shlex
import shutil
import re
import os
import time

class VirtualBox:
  def __init__(self, name, basefolder):
    self._name = name
    self._basefolder = basefolder
    self._cd = None

  def _vboxmanage(self, command):
    proc = subprocess.Popen(shlex.split('vboxmanage ' + command), stdout=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode is not 0:
      raise Exception(str(out) + '\n' + str(err))
    return out

  def _delete(self):
    out = self._vboxmanage('list vms')
    regex = re.compile('^"{0}"'.format(self._name), re.MULTILINE)
    if regex.search(str(out)):
      print 'Unregister vm "{0}"'.format(self._name)
      out = self._vboxmanage('unregistervm --delete "{0}"'.format(self._name))
    vm_path = os.path.join(self._basefolder, self._name)
    if os.path.isdir(vm_path):
      print 'Delete "{0}"'.format(vm_path)
      shutil.rmtree(vm_path)

  def _running(self):
    out = self._vboxmanage('list runningvms')
    regex = re.compile('^"{0}"'.format(self._name), re.MULTILINE)
    if regex.search(str(out)):
      return True
    return False

  def createvm(self, settings):
    self._delete()
    if not os.path.isdir(self._basefolder):
      os.makedirs(self._basefolder)
    print 'Create vm {0}'.format(self._name)
    self._vboxmanage('createvm --basefolder "{0}" --name "{1}" --ostype "{2}" --register'
                     .format(self._basefolder,
                             self._name,
                             settings['ostype']))

    modifyvm = str('modifyvm "{0}"' +
                   ' --memory {1} --vram {2} --cpus {3}' +
                   ' --rtcuseutc on --acpi on --ioapic on --accelerate3d on' +
                   ' --nic1 nat --natdnshostresolver1 on --audio none' +
                   ' --mouse usbtablet --keyboard usb --clipboard bidirectional')
    self._vboxmanage(modifyvm.format(self._name, settings['memory'], settings['vram'], settings['cpus']))

    hd_file = os.path.join(os.path.join(self._basefolder, self._name), self._name + '.vdi')
    self._vboxmanage('createhd --filename "{0}" --size 20480'.format(hd_file))
    self._vboxmanage('storagectl "{0}" --name "SATA Controller" --add sata --controller IntelAhci --sataportcount 5'.format(self._name))
    self._vboxmanage('storageattach "{0}" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "{1}"'.format(self._name, hd_file))
    self._vboxmanage('storagectl "{0}" --name "IDE Controller" --add ide --controller PIIX4'.format(self._name))

  def startvm(self):
    self._vboxmanage('startvm "{0}"'.format(self._name))

  def stopvm(self):
    self._vboxmanage('controlvm "{0}" acpipowerbutton'.format(self._name))

  def insert_cd(self, cd):
    if self._cd is None:
      self._vboxmanage('storageattach "{0}" --storagectl "IDE Controller" --port 1 --device 0 --type dvddrive --medium "{1}"'.format(self._name, cd))
      self._cd = cd

  def remove_cd(self):
    self._vboxmanage('storageattach "{0}" --storagectl "IDE Controller" --port 1 --device 0 --type dvddrive --medium emptydrive'.format(self._name))
    self._vboxmanage('closemedium dvd "{0}"'.format(self._cd))

  def wait_for_shutdown(self):
    while self._running():
      print '.',
      time.sleep(5)
    print

  def forward_ssh(self, ssh_port):
    try:
      self._vboxmanage('modifyvm "{0}" --natpf1 delete ssh'.format(self._name))
    except Exception:
      pass
    self._vboxmanage('modifyvm "{0}" --natpf1 "ssh,tcp,,{1},,22"'.format(self._name, ssh_port))

  def wait_for_started(self):
    count = 24
    running = False
    while count > 0:
      try:
        self._vboxmanage('guestcontrol "{0}" execute --username vagrant --password vagrant --wait-exit --image "/bin/ls"'.format(self._name))
        running = True
        break
      except Exception:
        time.sleep(5)
        count = count - 1
    if not running:
      raise Exception("Virtual box did not start.")


