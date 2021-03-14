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
        self.buffer = []  # one extra buffer for output purpose
        self.find_tuple_size()

    def find_tuple_size(self):
        x = open(self.left_relation, 'r')
        self.left_tuple_size = len(x.readline())
        x.close()
        x = open(self.right_relation, 'r')
        self.right_tuple_size = len(x.readline())
        x.close()

    def phase_one(self):
        left_file_size = os.stat(self.left_relation).st_size
        read_till = self.m * self.tuples * self.tuple_size
        files_to_be_created = math.ceil(left_file_size / read_till)
        print('left size : {a}'.format(a=left_file_size))
        print('files to be created : {a}'.format(a=files_to_be_created))
        self.left_sublist = files_to_be_created
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
        right_file_size = os.stat(self.right_relation).st_size
        files_to_be_created = math.ceil(right_file_size / read_till)
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
        to_read = self.tuples * self.tuple_size
        for i in range(self.left_sublist):
            file = open(self.left_relation, 'r')
            arr = file.readlines(to_read - 1)
            self.left_memory.append(arr)
            file.close()
        for i in range(self.right_sublist):
            file = open(self.right_relation, 'r')
            arr = file.readlines(to_read - 1)
            self.right_memory.append(arr)
            file.close()

    


if __name__ == '__main__':
    left_file = sys.argv[1]
    right_file = sys.argv[2]
    memory_buffers = int(sys.argv[3])
    # to get the tuple size we need to read one line from the file
    merge_join = MergeJoin(memory_buffers, left_file, right_file, 2)
    merge_join.phase_one()
