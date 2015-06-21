import subprocess
import urllib.request
import os
import shutil
import shlex

class InstallCD:
  def __init__(self, config):
    self._config = config
    self._iso_dir = os.path.join(self._config.build_dir, 'iso')
    self._mnt_dir = os.path.join(self._config.build_dir, 'mnt')
    self._download_dir = os.path.join(self._config.build_dir, 'download')
    self._install_cd = os.path.join(self._download_dir, self._config.install_cd_url.rsplit('/', 1)[1])

  def _setup_build_directory(self):
    print("Setup build directory: {0}".format(self._config.build_dir))
    if os.path.isdir(self._iso_dir):
      shutil.rmtree(self._iso_dir)

    if os.path.isdir(self._mnt_dir):
      shutil.rmtree(self._mnt_dir)
    os.makedirs(self._mnt_dir)

    if not os.path.isdir(self._download_dir):
      os.makedirs(self._download_dir)

  def _get_install_cd(self):
    if not os.path.isfile(self._install_cd):
      print("Download {0} from {1}".format(self._install_cd, self._config.install_cd_url))
      infile = urllib.request.urlopen(self._config.install_cd_url)
      outfile = open(self._install_cd, 'wb')
      outfile.write(infile.read())
      outfile.close()

  def _extract_install_cd(self):
    print("Extract install cd")
    proc = subprocess.Popen(['fuseiso', self._install_cd, self._mnt_dir])
    proc.communicate()

    shutil.copytree(self._mnt_dir, self._iso_dir, symlinks=True)

    proc = subprocess.Popen(['fusermount', '-u', self._mnt_dir])
    proc.communicate()
    proc = subprocess.Popen(['chmod', '-R', 'ug+rw', self._iso_dir])
    proc.communicate()

  def _apply_patches(self):
    print("Apply patches:")
    for patch in self._config.patches:
      print("  Replace {0}".format(patch))
      shutil.copy(os.path.join(self._config.patch_dir, patch), os.path.join(self._iso_dir, patch))

  def _create_iso(self):
    print("Create patched install cd")
    cmd = 'mkisofs -quiet -D -r -V "UBUNTU_SERVER" -cache-inodes -J -l -b "isolinux/isolinux.bin" -c "isolinux/boot.cat" -no-emul-boot -boot-load-size 4 -boot-info-table -o "{0}" "{1}"'.format(self._config.patched_cd, self._iso_dir)
    proc = subprocess.Popen(shlex.split(cmd))
    proc.communicate()

  def create(self):
    self._setup_build_directory()
    self._get_install_cd()
    self._extract_install_cd()
    self._apply_patches()
    self._create_iso()


