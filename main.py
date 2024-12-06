import sys
import numpy as np
import pandas as pd

storage_space = int(sys.orig_argv[2])
block_size = int(sys.orig_argv[3])
if storage_space % block_size == 0: block_num = storage_space // block_size
else: block_num = (storage_space // block_size) + 1
free_block_num = block_num
block_arr = np.zeros([block_num, block_size])
block_arr = block_arr.astype(int)
free_blocks = [i for i in range(block_num)]
file_ids = []
fat = {}

def main():
    global free_block_num, fat
    
    cont = input("\nThis is a sequential block allocation/deallocation simulator. You will be prompted to enter an ID number and size for each file, and the system will allocate and deallocate blocks as needed. Enter '0' as the file size for an existing file ID to remove it from the disk. A list of additional commands are as follows:\n\n - print: prints current state of the disk and FAT\n - clear: clears disk and FAT\n - compact: compacts files in disk\n - help: prints a list of available commands\n - exit: prints state and exits program\n\nWould you like to continue? (Y/N) ").lower()
    while cont not in ["y", "yes"]:
        if cont in ["n", "no"]:
            print("\nProgram has exited.\n")
            sys.exit()
        else:
            cont = input("ERROR: invalid input. Please enter Y/N: ")
    print()

    while True:
        file_id = input("Enter file ID (or other command): ")
        if not file_id.isnumeric():
            getCommand(file_id)
            continue
        file_size = input("Enter file size in bytes (or other command): ")
        if not file_size.isnumeric():
            getCommand(file_size)
            continue
        file_id = int(file_id)
        file_size = int(file_size)

        if file_size > 0:
            if file_size <= storage_space and file_size <= free_block_num * block_size:

                if file_id not in file_ids:
                    file_ids.append(file_id)
                else:
                    print("\nERROR: file ID already exists\n")
                    continue
                if file_id <= 0:
                    print("\nERROR: file ID must be ≥ 1\n")
                    continue

                if not enoughSpace(file_size):
                    print("\nNot enough contiguous space. Compacting...")
                    compact()
                    print("Compacting complete.\n")
                if file_size % block_size != 0:
                    block_num = (file_size // block_size) + 1
                else:
                    block_num = file_size // block_size

                fat[file_id] = {}
                blocks_left = block_num
                disk_block, file_block = 0, 0
                while blocks_left > 0:
                    if file_block <= block_num and block_arr[disk_block, 0] == 0:
                        block_arr[disk_block].fill(file_id)
                        fat[file_id].update({file_block: disk_block})
                        free_blocks.remove(disk_block)
                        free_block_num -= 1
                        blocks_left -= 1
                        file_block += 1
                    if disk_block < len(block_arr) - 1:
                        disk_block += 1
                    else:
                        break
            else:
                # JOB TOO LARGE
                if file_size > storage_space:
                    print("\nERROR: file size exceeds total disk space\n")
                else:
                    print("\nERROR: file size exceeds available disk space\n")
                continue
        else:
            # HANDLE 0
            if file_size == 0:
                remove(file_id)
            else:
                print("\nERROR: invalid size argument\n")
                continue

def getCommand(input):
    if input == "print":
        printState()
    elif input == "clear":
        clear()
        print("\nDisk has been cleared.\n")
    elif input == "compact":
        compact()
        print("\nDisk has been compacted.\n")
    elif input == "help":
        print("\nAvailable commands:\n\n - print: prints current state of the disk and FAT\n - clear: clears disk and FAT\n - compact: compacts files in disk\n - help: prints a list of available commands\n - exit: prints state and exits program\n")
    elif input == "exit":
        printState()
        print("\nProgram has exited.\n")
        sys.exit()
    else:
        print("\nERROR: invalid command\n")

def clear():
    global free_blocks, free_block_num, file_ids, fat

    block_arr.fill(0)
    free_block_num = block_num
    free_blocks = [i for i in range(block_num)]
    file_ids = []
    fat = {}

def enoughSpace(size):
    if not free_blocks: return False
    free = 1
    if size % block_size == 0: block_num = size // block_size
    else: block_num = (size // block_size) + 1
    if free == block_num: return True

    for i in range(len(free_blocks) - 1):
        cur = free_blocks[i]
        for j in range(i + 1, len(free_blocks)):
            if free_blocks[j] == cur + 1:
                cur += 1
                free += 1
                if free == block_num: return True
            else:
                free = 0
                break
    return False

def compact():
    global fat

    block_list = []
    for i in range(len(block_arr)):
        if block_arr[i, 0] != 0:
            block_list.append(block_arr[i, 0])
    
    block_arr.fill(0)
    free_blocks.clear()
    key = 0
    last_id = block_list[0]
    for i in range(len(block_arr)):
        if i < len(block_list):
            block_arr[i].fill(block_list[i])
            fat[block_list[i]].update({key: i})
            key += 1
            if block_list[i] != last_id:
                key = 0
            last_id = block_list[i]
        else:
            free_blocks.append(i)

    fat = {outer_key: {inner_key: value for inner_key, value in zip(inner_dict.keys(), reversed(inner_dict.values()))} for outer_key, inner_dict in fat.items()}

def remove(file_id):
    global free_block_num

    if file_id in file_ids:
        file_ids.remove(file_id)
    else:
        print("\nERROR: file ID does not exist\n")
        return

    fat.pop(file_id)
    for block in range(len(block_arr)):
        if block_arr[block, 0] == file_id:
            free_blocks.append(block)
            free_block_num += 1
            block_arr[block].fill(0)
    print(f"\nFile {file_id} successfully removed.\n")

def printState():
    print()
    columns = []
    for i in range(block_num):
        columns.append(f"File Block {i + 1}")
    block_table = pd.DataFrame(columns=columns)

    for file_ID in file_ids:
        disk_blocks = list(fat[file_ID].values())
        for i in range(len(disk_blocks)):
            disk_blocks[i] = f"Disk Block {disk_blocks[i]}"
        length = len(disk_blocks)
        if(length < block_num):
            diff = block_num - length
            for i in range(diff):
                disk_blocks.append("None")
        block_table.loc[f"File {file_ID}"] = disk_blocks

    print(block_table)
    print()

    print("Disk Block".ljust(20) + "File ID".ljust(20))
    for i in range(len(block_arr)):
        print(f"{i+1}".ljust(20) + str(block_arr[i, 0]))
    print()

main()
