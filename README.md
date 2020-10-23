# artix-on-luks-btrfs

Run `sh preinstall.sh`, then `python install.py` should work.
Run `artools-chroot /mnt /bin/bash`
Run `python /root/iamchroot.py`. When `iamchroot.py` finishes, `exit` the chroot, `umount -R /mnt` if you want, and `poweroff`.

