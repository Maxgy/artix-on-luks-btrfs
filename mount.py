#!/usr/bin/env python

import sys

from subprocess import run, check_output

disk = ""
while True:
    while True:
        run("fdisk -l", shell=True)
        print("\nDisk to mount", end=": ")
        disk = input().strip()
        if len(disk) > 0:
            break
    break

part1 = ""
part2 = ""
part3 = ""
if "nvme" in disk:
    part1 = disk + "p1"
    part2 = disk + "p2"
    part3 = disk + "p3"
else:
    part1 = disk + "1"
    part2 = disk + "2"
    part3 = disk + "3"
# Setup encrypted partitions
cryptpass = ""
while True:
    print("Encryption password", end=": ")
    cryptpass = input().strip()
    print("Repeat password", end=": ")
    second = input().strip()

    if cryptpass == second and len(cryptpass) > 1:
        break

run(f"yes '{cryptpass}' | cryptsetup open {part3} cryptroot", shell=True)
run(f"yes '{cryptpass}' | cryptsetup open {part2} cryptswap", shell=True)

# Mount subvolumes and boot
run("mount -o compress=zstd,subvol=@ /dev/mapper/cryptroot /mnt", shell=True)
run("mount -o compress=zstd,subvol=@snapshots /dev/mapper/cryptroot /mnt/.snapshots", shell=True)
run("mount -o compress=zstd,subvol=@home /dev/mapper/cryptroot /mnt/home", shell=True)
run(f"mount {part1} /mnt/boot", shell=True)
