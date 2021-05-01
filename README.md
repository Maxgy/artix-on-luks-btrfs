# artix-on-luks-btrfs

A stupid installer for Artix Linux

## Usage

Use `sh install.sh` to run the installer.

## Assumptions

- These scripts assume you are already booted into the Artix live disk or you at least have `artools` (it may be called something else now) on your system and have loaded all of the scripts in some way. In the live environment, I just used another USB drive that had the scripts and mounted it, but you can probably use `git` or `wget` the raw files directly.
- It also assumes you want what it wants and adhere to the occasional instructions it gives you, the user, to perform.
- The scripts also _*don't*_ make assumptions about your hardware and will automatically use both AMD and Intel ucode initrd images.

## What you get

An encrypted Artix Linux system with OpenRC and Btrfs subvols for root, snapshots, and home. Only necessary packages are installed with a few minor exceptions for flavor or the install process (`python`, `zsh`, `neovim`, `neofetch`). Also note that `install.py` and `iamchroot.py` are copied to `/root` during the installation process.

Post-installation networking is done with `connman`.

### Partition Scheme

| \#  | Size | Type             | LUKS | FS    |
| --- | ---- | ---------------- | ---- | ----- |
| 1   | 1G   | EFI System       |      | fat32 |
| 2   | ~16G | Linux swap       | \*   | swap  |
| 3   | FREE | Linux filesystem | \*   | btrfs |

### Btrfs subvolumes

| \#  | Name       | Mount       |
| --- | ---------- | ----------- |
| 1   | @          | /           |
| 2   | @snapshots | /.snapshots |
| 3   | @home      | /home       |

### Software

| Feature       | Name    |
| ------------- | ------- |
| Boot loader   | rEFInd  |
| Filesystem    | Btrfs   |
| Init Software | OpenRC  |
| Networking    | connman |
| Shell         | Zsh     |
