# artix-on-luks-btrfs

Run `sh preinstall.sh`, then `python install.py` should work. Run `python /root/iamchroot.py` when `install.py` finishes and drops you in the new system. When `iamchroot.py` finishes, `exit` the chroot, `umount -R /mnt` if you want, and `poweroff`.

