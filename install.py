#!/usr/bin/env python

'''
sudo su
rfkill unblock wifi
ip link set WLAN0 up
connmanctl
    technologies
    scan wifi
    services
    agent on
    connect WIFI_NAME
        PASS
    quit
---
loadkeys us
ls /sys/firmware/efi/efivars
---
cfdisk /dev/sdX
    gpt
    1 New 1G 'EFI System'
    2 New 16 GB 'Linux swap'
    3 New *FREE 'Linux filesystem'
    Write yes Quit
---
cryptsetup -y -v luksFormat /dev/sdX3
cryptsetup open /dev/sdX3 cryptroot
cryptsetup -y -v luksFormat /dev/sdX1
cryptsetup open /dev/sdX1 cryptswap
mkswap -L myswap /dev/mapper/cryptswap
mkfs.fat -F 32 /dev/sdX1
mkfs.btrfs -L btrfsroot /dev/mapper/cryptroot
---
mount /dev/mapper/cryptroot /mnt
btrfs subvolume create /mnt/@
btrfs subvolume create /mnt/@snapshots
btrfs subvolume create /mnt/@home
umount -R /mnt
---
mount -o compress=zstd,subvol=@ /dev/mapper/cryptroot /mnt
mkdir /mnt/.snapshots
mkdir /mnt/home
mount -o compress=zstd,subvol=@snapshots /dev/mapper/cryptroot /mnt/.snapshots
mount -o compress=zstd,subvol=@home /dev/mapper/cryptroot /mnt/home
mkdir /mnt/boot
mount /dev/sdX1 /mnt/boot
---
basestrap /mnt base base-devel openrc cryptsetup btrfs-progs
basestrap /mnt linux linux-firmware linux-headers
fstabgen -U /mnt >> /mnt/etc/fstab
artools-chroot /mnt /bin/bash
---
ln -sf /usr/share/zoneinfo/REGION/CITY /etc/localtime
hwclock --systohc
pacman -Syu neovim bat fd exa ripgrep neofetch
---
nvim /etc/pacman.d/gnupg/gpg.conf
    keyserver hkp://keyserver.ubuntu.com
pacman-key --populate artix
---
nvim /etc/locale.gen
    #en_US
locale-gen
nvim /etc/locale.conf
    LANG=en_US.UTF-8
nvim /etc/vconsole.conf
    KEYMAP=us
nvim /etc/hostname
    HOSTNAME
nvim /etc/hosts
    127.0.0.1   localhost
    ::1         localhost
    127.0.1.1   HOSTNAME.localdomain    HOSTNAME
---
pacman -S efibootmgr refind amd-ucode intel-ucode
nvim /etc/mkinitcpio.conf
    HOOKS=(... autodetect keyboard keymap modconf block encrypt filesystems ...)
mkinitcpio -P
blkid > /root/ids.txt
refind-install
refind-install --usedefault /dev/sdX1
nvim /boot/refind_linux.conf
    cryptdevice=UUID=(sdX3):cryptroot root=/dev/mapper/cryptroot rootflags=subvol=@ rw initrd=amd-ucode.img initrd=intel-ucode.img initrd=initramfs-linux.img
nvim /etc/local.d/local.start
    rfkill unblock wifi
    neofetch >| /etc/issue
chmod +x /etc/local.d/local.start
---
passwd
pacman -S zsh openrc-zsh-completions zsh-autosuggestions zsh-completions zsh-syntax-highlighting
rm /etc/skel/.bash*
useradd -D -s /bin/zsh
useradd -m USERNAME
passwd USERNAME
usermod -a -G wheel USERNAME
usermod -a -G video USERNAME
EDITOR=nvim visudo
    #%wheel
pacman -S dhcpcd wpa_supplicant connman-openrc
rc-update add connmand
nvim /etc/motd
nvim /etc/fstab
    #remove extra subvols
    # /dev/mapper/cryptswap  swap  swap  defaults 0 0
nvim /etc/initcpio/hooks/openswap
    run_hook() {
        cryptsetup open /dev/disk/by-uuid/SWAPUUID cryptswap
    }
nvim /etc/initcpio/install/openswap
    build() {
        add_runscript
    }
nvim /etc/mkinitcpio.conf
    HOOKS = (... encrypt openswap resume filesystems ...)
mkinitcpio -P
nvim /boot/refind_linux.conf
    # resume=/dev/mapper/cryptswap
exit
---
trusted
cargo-update
starship
.dotfiles
spacevim
'''

import sys

from subprocess import run, check_output

print("Installing Artix Linux with LUKS and Btrfs...\n")

# Check boot mode
if len(check_output("ls /sys/firmware/efi/efivars", shell=True)) < 8:
    print("\nNot booted in UEFI mode, aborting...")
    sys.exit()

# Load keymap
print("\nKeymap", end=" (us): ")
keymap = input().strip()
if len(keymap) < 2:
    keymap = "us"
run(f"loadkeys {keymap}", shell=True)

# Partition disk
disk = ""
while True:
    while True:
        run("fdisk -l", shell=True)
        print("\nDisk to install to", end=": ")
        disk = input().strip()
        if len(disk) > 0:
            break
    print('''Partition scheme:
        gpt
        1 New 1G 'EFI System'
        2 New 16G 'Linux swap'
        3 New *FREE 'Linux filesystem'
        Write yes Quit
    ''')
    input()
    run(f"cfdisk {disk}", shell=True)
    
    print(f"\nInstall on '{disk}'?", end=" (y/N): ")
    choice = input().strip()
    if len(choice) > 0 and choice[0] == "y":
        break

# Setup encrypted partitions
cryptpass = ""
while True:
    print("Encryption password", end=": ")
    cryptpass = input().strip()
    print("Repeat password", end=": ")
    second = input().strip()

    if cryptpass == second and len(cryptpass) > 1:
        break
run(f"printf '{cryptpass}' > cryptpass.txt", shell=True)
run("cryptsetup close /dev/mapper/cryptroot", shell=True),
run("cryptsetup close /dev/mapper/cryptswap", shell=True),
   
run(f"yes YES | cryptsetup luksFormat {disk}3 cryptpass.txt", shell=True)
run(f"yes YES | cryptsetup luksFormat {disk}2 cryptpass.txt", shell=True)

run("rm cryptpass.txt", shell=True)

run(f"yes '{cryptpass}' | cryptsetup open {disk}3 cryptroot", shell=True)
run(f"yes '{cryptpass}' | cryptsetup open {disk}2 cryptswap", shell=True)

# Format partitions
run("mkswap /dev/mapper/cryptswap", shell=True)
run(f"mkfs.fat -F 32 {disk}1", shell=True)
run("mkfs.btrfs /dev/mapper/cryptroot", shell=True)

# Create subvolumes
run("umount -R /mnt/boot", shell=True)
run("umount -R /mnt", shell=True)
run("rm -rf /mnt", shell=True)
run("mkdir /mnt", shell=True)
run("mount /dev/mapper/cryptroot /mnt", shell=True)
run("btrfs subvolume create /mnt/@", shell=True)
run("btrfs subvolume create /mnt/@snapshots", shell=True)
run("btrfs subvolume create /mnt/@home", shell=True)
run("umount -R /mnt", shell=True)

# Mount subvolumes and boot
run("mount -o compress=zstd,subvol=@ /dev/mapper/cryptroot /mnt", shell=True)
run("mkdir /mnt/.snapshots", shell=True)
run("mkdir /mnt/home", shell=True)
run("mount -o compress=zstd,subvol=@snapshots /dev/mapper/cryptroot /mnt/.snapshots", shell=True)
run("mount -o compress=zstd,subvol=@home /dev/mapper/cryptroot /mnt/home", shell=True)
run("mkdir /mnt/boot", shell=True)
run(f"mount {disk}1 /mnt/boot", shell=True)

# Install base system and kernel
run("basestrap /mnt base base-devel openrc cryptsetup btrfs-progs python neovim", shell=True)
run("basestrap /mnt linux linux-firmware linux-headers", shell=True)
run("fstabgen -U /mnt >> /mnt/etc/fstab", shell=True)

# Finish
run("cp install.py /mnt/root/", shell=True)
run("cp iamchroot.py /mnt/root/", shell=True)
print("Run `artools-chroot /mnt /bin/bash`")
print("\nRun `python /root/iamchroot.py` once you are in the new system.")
