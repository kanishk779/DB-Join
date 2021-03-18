import os
import math
import sys


class MergeJoin:

    def __init__(self, m, left_relation, right_relation, tuples):
        self.m = m  # main memory buffers
        self.tuples = tuples  # number of tuples in one block
        self.left_tuple_size = 0  # size of each tuple in bytes for left relation
        self.right_tuple_size = 0  # size of each tuple in bytes for right relation
        self.left_relation = left_relation  # name of left relation
        self.right_relation = right_relation  # name of right relation
        self.left_sublist = 0
        self.right_sublist = 0
        self.left_memory = []  # stores the left sorted sublist first blocks
        self.right_memory = []  # stores the right sorted sublist first blocks
        self.buffer = []  # one extra buffer for output purpose, list of strings
        self.left_sublist_offsets = []
        self.right_sublist_offsets = []
        self.left_file_list = []
        self.right_file_list = []
        self.left_sublist_read = []  # how much data we have actually read from each left sublist
        self.right_sublist_read = []  # how much data we have actually read from each right sublist
        self.get_next_index = 0
        self.read_file = open('output.txt', 'r')
        self.FOUND = True
        self.find_tuple_size()

    def find_tuple_size(self):
        x = open(self.left_relation, 'r')
        self.left_tuple_size = len(x.readline())
        x.close()
        x = open(self.right_relation, 'r')
        self.right_tuple_size = len(x.readline())
        x.close()

    def write_out(self):
        out_file = open('output.txt', 'a')
        for line in self.buffer:
            out_file.write(line)
        self.buffer = []

    def open(self):
        left_file_size = os.stat(self.left_relation).st_size
        right_file_size = os.stat(self.right_relation).st_size
        block_left = (left_file_size + self.tuples * self.left_tuple_size - 1) // (self.tuples * self.left_tuple_size)
        block_right = (right_file_size + self.tuples * self.right_tuple_size - 1) // (self.tuples * self.right_tuple_size)
        if block_left + block_right < (self.m * self.m):
            self.phase_one()
        else:
            raise NotImplementedError('Not possible as B(R) + B(S) >= M^2')

    def get_next(self):
        if self.get_next_index == self.tuples:
            arr = self.read_file.readlines(self.tuples * self.left_tuple_size - 1)  # we can choose either left or right
            if len(arr) == 0:
                print('All data has been read')
                self.FOUND = False
            else:
                self.buffer = arr
                self.get_next_index = 1
                return self.buffer[self.get_next_index - 1]
        else:
            self.get_next_index += 1
            return self.buffer[self.get_next_index - 1]

    def close(self):
        self.read_file.close()
        for i in range(self.left_sublist):
            self.left_file_list[i].close()
        for i in range(self.right_sublist):
            self.right_file_list[i].close()

    def phase_one(self):
        left_file_size = os.stat(self.left_relation).st_size
        read_till = self.m * self.tuples * self.left_tuple_size
        files_to_be_created = math.ceil(left_file_size / read_till)
        
        self.left_sublist = files_to_be_created
        self.left_sublist_offsets = [0] * files_to_be_created  # initially all the sublist start from first block
        left = open(self.left_relation, 'r')
        for i in range(files_to_be_created):
            arr = left.readlines(read_till-1)  # need to subtract one otherwise one more line will be read
            dump_file = open(self.left_relation + str(i), 'w')
            brr = []
            for line in arr:
                temp = line[:-1]
                x, y = temp.split(' ')
                brr.append((x, y))
            brr.sort(key=lambda k: k[1])
            for line in brr:
                x, y = line
                to_write = x + ' ' + y
                dump_file.write(to_write + '\n')
            dump_file.close()
        left.close()
        read_till = self.m * self.tuples * self.right_tuple_size
        right_file_size = os.stat(self.right_relation).st_size
        files_to_be_created = math.ceil(right_file_size / read_till)
        self.right_sublist_offsets = [0] * files_to_be_created  # initially all the sublist start from first block
        self.right_sublist_read = [0] * files_to_be_created
        self.right_sublist = files_to_be_created
        right = open(self.right_relation, 'r')
        for i in range(files_to_be_created):
            arr = right.readlines(read_till-1)
            dump_file = open(self.right_relation + str(i), 'w')
            brr = []
            for line in arr:
                temp = line[:-1]
                x, y = temp.split(' ')
                brr.append((x, y))
            brr.sort(key=lambda k: k[0])
            for line in brr:
                x, y = line
                to_write = x + ' ' + y
                dump_file.write(to_write + '\n')
            dump_file.close()
        right.close()

    def initialise_list(self):
        # read one block from each of the sorted file
        to_read = self.tuples * self.left_tuple_size
        for i in range(self.left_sublist):
            file = open(self.left_relation + str(i), 'r')
            arr = file.readlines(to_read - 1)
            self.left_memory.append(arr)
            self.left_file_list.append(file)
        to_read = self.tuples * self.right_tuple_size
        for i in range(self.right_sublist):
            file = open(self.right_relation + str(i), 'r')
            arr = file.readlines(to_read - 1)
            self.right_memory.append(arr)
            self.right_file_list.append(file)

    def join(self):
        # find the minimum from the above
        self.initialise_list()
        left_not_processed = [1] * self.left_sublist
        right_not_processed = [1] * self.right_sublist
        cnt = 0
        while any(left_not_processed) and any(right_not_processed):
            xx = ""
            left_min = "~"  # since it is the largest character
            for i in range(self.left_sublist):
                if left_not_processed[i] == 0:
                    continue  # continue if the sublist has been completely read
                ind = self.left_sublist_offsets[i]
                if ind == len(self.left_memory[i]):
                    # re fill the block
                    to_read = self.tuples * self.left_tuple_size
                    arr = self.left_file_list[i].readlines(to_read - 1)
                    if len(arr) == 0:
                        left_not_processed[i] = 0
                        continue
                    ind = 0
                    self.left_sublist_offsets[i] = ind
                    self.left_memory[i] = arr
                temp = self.left_memory[i][ind]
                temp = temp[:-1]
                x, y = temp.split(' ')
                if y < left_min:
                    left_min = y
                    xx = x
            right_min = "~"
            for i in range(self.right_sublist):
                if right_not_processed[i] == 0:
                    continue
                ind = self.right_sublist_offsets[i]
                if ind == len(self.right_memory[i]):
                    # re fill the block
                    to_read = self.tuples * self.right_tuple_size
                    arr = self.right_file_list[i].readlines(to_read - 1)
                    if len(arr) == 0:
                        right_not_processed[i] = 0
                        continue
                    ind = 0
                    self.right_sublist_offsets[i] = ind
                    self.right_memory[i] = arr
                temp = self.right_memory[i][ind]
                temp = temp[:-1]
                y, z = temp.split(' ')
                if y < right_min:
                    right_min = y

            if left_min < right_min:
                for i in range(self.left_sublist):
                    ind = self.left_sublist_offsets[i]
                    # remove all the tuples with Y = left_min
                    while ind < len(self.left_memory[i]):
                        temp = self.left_memory[i][ind]
                        temp = temp[:-1]
                        x, y = temp.split(' ')
                        if y == left_min:
                            self.left_sublist_offsets[i] += 1
                            ind += 1
                        else:
                            break
            elif right_min < left_min:
                for i in range(self.right_sublist):
                    ind = self.right_sublist_offsets[i]
                    # remove all the tuple with Y = right_min
                    while ind < len(self.right_memory[i]):
                        temp = self.right_memory[i][ind]
                        temp = temp[:-1]
                        y, z = temp.split(' ')
                        if y == right_min:
                            self.right_sublist_offsets[i] += 1
                            self.right_sublist_read[i] += self.right_tuple_size
                            ind += 1
                        else:
                            break
            else:
                # the left min will join with all the right ones
                # just remove only one tuple with Y = left_min
                self.join_right(xx, left_min)
                for i in range(self.left_sublist):
                    ind = self.left_sublist_offsets[i]
                    if ind == len(self.left_memory[i]):
                        to_read = self.tuples * self.left_tuple_size
                        arr = self.left_file_list[i].readlines(to_read - 1)
                        self.left_sublist_offsets[i] = 0
                        ind = 0
                        if len(arr) == 0:
                            left_not_processed[i] = 0
                        else:
                            self.left_memory[i] = arr
                    temp = self.left_memory[i][ind]
                    temp = temp[:-1]
                    x, y = temp.split(' ')
                    if y == left_min:
                        ind += 1
                        self.left_sublist_offsets[i] += 1
                        if ind == len(self.left_memory[i]):
                            self.left_sublist_offsets[i] = 0
                            to_read = self.tuples * self.left_tuple_size
                            arr = self.left_file_list[i].readlines(to_read - 1)
                            if len(arr) == 0:
                                left_not_processed[i] = 0
                            else:
                                self.left_memory[i] = arr
                        break
        # collect all the tuples with Y = the above found minimum

    def join_right(self, xx, left_y):
        """
        join x, y with the right table
        :return: nothing
        """
        files = []
        for i in range(self.right_sublist):
            a = open(self.right_relation + str(i), 'r')
            a.seek(self.right_sublist_read[i])
            files.append(a)
        # needs to maintain the pointers for right file as well
        for i in range(self.right_sublist):
            ind = self.right_sublist_offsets[i]
            temp_mem = self.right_memory[i]
            if ind == len(temp_mem):
                to_read = self.tuples * self.right_tuple_size
                arr = files[i].readlines(to_read - 1)
                if len(arr) == 0:
                    continue
                else:
                    temp_mem = arr
                ind = 0
            temp = temp_mem[ind]
            y, z = temp.split(' ')

            while y == left_y:
                to_write = xx + ' ' + y + ' ' + z
                self.buffer.append(to_write)
                if len(self.buffer) == self.tuples:
                    self.write_out()
                ind += 1
                if ind == len(temp_mem):
                    # need to re fill the block
                    to_read = self.tuples * self.right_tuple_size
                    arr = files[i].readlines(to_read - 1)
                    if len(arr) == 0:
                        break
                    else:
                        temp_mem = arr
                    ind = 0
                temp = temp_mem[ind]
                y, z = temp.split(' ')
            self.write_out()  # write whatever is left


class HashJoin:

    def __init__(self, m, left_relation, right_relation, tuples):
        self.m = m  # main memory buffers
        self.tuples = tuples  # number of tuples in one block
        self.left_tuple_size = 0  # size of each tuple in bytes for left relation
        self.right_tuple_size = 0  # size of each tuple in bytes for right relation
        self.left_relation = left_relation  # name of left relation
        self.right_relation = right_relation  # name of right relation
        self.get_next_index = 0
        self.read_file = open('output.txt', 'r')
        self.buffer = []  # one extra buffer for output purpose, list of strings
        self.FOUND = True
        self.find_tuple_size()

    def find_tuple_size(self):
        x = open(self.left_relation, 'r')
        self.left_tuple_size = len(x.readline())
        x.close()
        x = open(self.right_relation, 'r')
        self.right_tuple_size = len(x.readline())
        x.close()

    def write_out(self):
        out_file = open('output.txt', 'a')
        for line in self.buffer:
            out_file.write(line)
        self.buffer = []

    def get_next(self):
        if self.get_next_index == self.tuples:
            arr = self.read_file.readlines(self.tuples * self.left_tuple_size - 1)  # we can choose either left or right
            if len(arr) == 0:
                print('All data has been read')
                self.FOUND = False
            else:
                self.buffer = arr
                self.get_next_index = 1
                return self.buffer[self.get_next_index - 1]
        else:
            self.get_next_index += 1
            return self.buffer[self.get_next_index - 1]

    def close(self):
        self.read_file.close()

    def open(self):
        left_file_size = os.stat(self.left_relation).st_size
        right_file_size = os.stat(self.right_relation).st_size
        block_left = (left_file_size + self.tuples*self.left_tuple_size - 1) // (self.tuples * self.left_tuple_size)
        block_right = (right_file_size + self.tuples*self.right_tuple_size - 1) // (self.tuples * self.right_tuple_size)
        if block_left + block_right >= (self.m * self.m):
            raise NotImplementedError('Not possible as B(R) + B(S) >= M^2')

        file = open(self.left_relation, 'r')
        hashed_list = dict()
        while True:
            to_read = self.tuples * self.left_tuple_size
            arr = file.readlines(to_read-1)
            if len(arr) == 0:
                break
            for line in arr:
                temp = line[:-1]
                x, y = temp.split(' ')
                num = self.give_hash(y)
                if num in hashed_list:
                    hashed_list[num].append(line)
                else:
                    hashed_list[num] = [line]
                if len(hashed_list[num]) == self.tuples:
                    append_file = open(self.left_relation + str(num), 'a')
                    for data in hashed_list[num]:
                        append_file.write(data)
                    hashed_list[num] = []
                    append_file.close()  # close the file
        for i in range(self.m):
            append_file = open(self.left_relation + str(i), 'a')
            for data in hashed_list[i]:
                append_file.write(data)
            hashed_list[i] = []
            append_file.close()
        file.close()

        file = open(self.right_relation, 'r')
        while True:
            to_read = self.tuples * self.right_tuple_size
            arr = file.readlines(to_read - 1)
            if len(arr) == 0:
                break
            for line in arr:
                y, z = line.split(' ')
                num = self.give_hash(y)
                if num in hashed_list:
                    hashed_list[num].append(line)
                else:
                    hashed_list[num] = [line]
                if len(hashed_list[num]) == self.tuples:
                    append_file = open(self.right_relation + str(num), 'a')
                    for data in hashed_list[num]:
                        append_file.write(data)
                    hashed_list[num] = []
                    append_file.close()  # close the file
        for i in range(self.m):
            append_file = open(self.right_relation + str(i), 'a')
            for data in hashed_list[i]:
                append_file.write(data)
            hashed_list[i] = []
            append_file.close()
        file.close()

    def join(self):
        # we can assume that the R_i or S_i will fill in the main memory
        # read page 294
        # since we have hashed into self.m buckets, we need to iterate over each of them
        for i in range(self.m):
            # get the sizes of R_i and S_i and load the smaller one into the memory
            left_file_size = os.stat(self.left_relation + str(i)).st_size
            right_file_size = os.stat(self.right_relation + str(i)).st_size
            if left_file_size < right_file_size:
                left_f = open(self.left_relation + str(i), 'r')
                lines = left_f.readlines()
                # create a search structure over the common column i.e Y
                # a dict with key = Y and a list of all the X values
                search_structure = dict()
                for line in lines:
                    temp = line[:-1]
                    x, y = temp.split(' ')
                    if y in search_structure:
                        search_structure[y].append(x)
                    else:
                        search_structure[y] = [x]  # initialise a list if not present
                # read each block of right relation and for each tuple find all tuples which can join
                right_f = open(self.right_relation + str(i), 'r')
                while True:
                    right_buffer = right_f.readlines(self.tuples * self.right_tuple_size - 1)
                    if len(right_buffer) > 0:
                        for line in right_buffer:
                            # use the search_structure
                            y, z = line.split(' ')
                            if y in search_structure:
                                for x in search_structure[y]:
                                    to_write = x + ' ' + y + ' ' + z
                                    self.buffer.append(to_write)
                                    if len(self.buffer) > self.tuples:
                                        self.write_out()
                            else:
                                pass
                        self.write_out()  # write the remaining data in buffer to the disk
                    else:
                        break
            else:
                right_f = open(self.right_relation + str(i), 'r')
                lines = right_f.readlines()
                search_structure = dict()
                for line in lines:
                    y, z = line.split(' ')
                    if y in search_structure:
                        search_structure[y].append(z)
                    else:
                        search_structure[y] = [z]
                left_f = open(self.left_relation + str(i), 'r')
                while True:
                    left_buffer = left_f.readlines(self.tuples * self.left_tuple_size - 1)
                    if len(left_buffer) > 0:
                        for line in left_buffer:
                            # use search_structure
                            temp = line[:-1]
                            x, y = temp.split(' ')
                            if y in search_structure:
                                for z in search_structure[y]:
                                    to_write = x + ' ' + y + ' ' + z
                                    self.buffer.append(to_write)
                                    if len(self.buffer) > self.tuples:
                                        self.write_out()
                            else:
                                pass
                        self.write_out()  # write the remaining data in buffer to the disk
                    else:
                        break

    def give_hash(self, y):
        # returns an integer
        power_p = 1
        p = 31
        mod = self.m
        hash_val = 0
        for char in y:
            hash_val = (hash_val + (ord(char) - 96)*power_p) % mod
            power_p = (power_p * p) % mod

        return hash_val


if __name__ == '__main__':
    left_file = sys.argv[1]
    right_file = sys.argv[2]
    which = sys.argv[3]
    memory_buffers = int(sys.argv[4])
    temp_file2 = open('temp2.txt', 'r+')
    temp_file2.truncate(0)
    # to get the tuple size we need to read one line from the file
    if which == 'sort':
        merge_join = MergeJoin(memory_buffers, left_file, right_file, 40)
        merge_join.open()
        merge_join.join()
        merge_join.close()
    else:
        hash_join = HashJoin(memory_buffers, left_file, right_file, 40)
        hash_join.open()
        hash_join.join()
        hash_join.close()
