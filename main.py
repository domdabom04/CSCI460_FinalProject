import sys
import numpy as np
import pandas as pd

np.set_printoptions(threshold=sys.maxsize)

storage_space = int(sys.orig_argv[2])
block_size = int(sys.orig_argv[3])
if storage_space % block_size == 0: block_num = storage_space // block_size
else: block_num = (storage_space // block_size) + 1
free_block_num = block_num

block_arr = np.zeros([block_num, block_size])
block_arr = block_arr.astype(int)
free_blocks = [i for i in range(block_num)]
fat = {}

def main():

    global block_arr, free_blocks, free_block_num, fat
    cont = input("\nThis is a block allocation/deallocation simulator. you will be prompted to enter an ID number and size for each file, and the system will allocate and deallocate blocks as needed. Type 'print' at any time to print the current state, or 'exit' at any time to exit the program. Would you like to continue? (Y/N) ").lower()
    while cont not in ["y", "yes"]:
        if cont in ["n", "no"]: break
        else: pass
    print("\n")

    while True:
        file_id = input("Enter file ID (or other command): ")
        if file_id == "print":
            print_state()
            continue
        elif file_id == "exit":
            print("Program has exited.")
            break
        file_size = input("Enter file size in bytes (or other command): ")
        if file_size == "print":
            print_state()
            continue
        elif file_size == "exit":
            print("Program has exited.")
            break
        file_id = int(file_id)
        file_size = int(file_size)

        if file_size > 0:
            if file_size <= storage_space and file_size <= free_block_num * block_size:
                if not enoughSpace(file_size):
                    compact()
                if file_size % block_size != 0:
                    block_num = (file_size // block_size) + 1
                else:
                    block_num = file_size // block_size

                fat[file_id] = {}
                blocks_left = block_num
                storage_block, file_block = 0, 0
                while blocks_left > 0:
                    if file_block <= block_num:
                        if block_arr[storage_block, 0] == 0:
                            block_arr[storage_block].fill(file_id)
                            fat[file_id].update({file_block: storage_block})
                            free_blocks.remove(storage_block)
                            free_block_num -= 1
                            blocks_left -= 1
                            file_block += 1
                    if storage_block < len(block_arr) - 1: # Necessary?
                        storage_block += 1
                    else:
                        #print("ERROR: block index exceeds total number of blocks.")
                        break
            else:
                # JOB TOO LARGE
                if file_size > storage_space:
                    print("ERROR: file size exceeds total storage space")
                else:
                    print("ERROR: file size exceeds available storage space")
                continue
        else:
            # HANDLE 0
            if file_size == 0:
                remove(file_id)
            else:
                print("ERROR: invalid size/cmd argument.")
                continue

    print_state()

    return

def enoughSpace(size):
    free = 0
    if size % block_size == 0: block_num = size // block_size
    else: block_num = (size // block_size) + 1
    for i in range(len(free_blocks)):
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
            block_list.append(block_arr[i][0])
    
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

    fat = {
        outer_key: {inner_key: value for inner_key, value in zip(inner_dict.keys(), reversed(inner_dict.values()))}
        for outer_key, inner_dict in fat.items()
    }

def remove(file_id):

    global block_arr, free_blocks, free_block_num

    fat.pop(file_id)
    for block in range(len(block_arr)):
        if block_arr[block, 0] == file_id:
            free_blocks.append(block)
            free_block_num += 1
            block_arr[block].fill(0)

def print_state():

    '''page_table_df = pd.DataFrame.from_dict(fat, orient="index")
    page_table_df.fillna(-100000, inplace=True)
    page_table_df = page_table_df.astype(int)
    page_table_df = page_table_df.applymap(lambda x: "| block" + str(x).rjust(3) if type(x) == int else "Suspended")
    page_table_df.index.name = "File ID"
    page_table_df.columns = [f"Block {i}" for i in range(page_table_df.shape[1])]
    #page_table_df["   Internal Fragmentation"] = int_frag

    frame_df = pd.DataFrame(block_arr[:, 0], columns=["File ID"])
    frame_df.index.name = "Block Number"
    frame_df = frame_df.iloc[0:]

    #print("\n\nPAGING SYSTEM SIMULATOR:\n\nThis system emulates a simple file system. Printed below are the file_block tables for each process (job) in the system, as well as the internal fragmentation for each job. Free frames are denoted as 'FREE'. Note that a negative storage_block value indicates a storage_block in secondary storage. Below that is a table showing each storage_block in main memory and the ID of the job occupying that storage_block. Free frames are also denoted as 'FREE'.")

    print("\nFile Allocation Tables:\n")
    print(page_table_df.replace(str("| storage_block-100000"), "|     FREE").to_string())

    print("\n\nStorage:\n")
    print(frame_df.replace(0, "FREE").to_string())
    print("\n")'''

    for key, value in fat.items():
        print(f"Key: {key}   Value: {value}")
    print(block_arr)

main()
