import os
import math
import sys


class MergeJoin:

    def __init__(self, m, left_relation, right_relation, tuples, tuple_size):
        self.m = m  # main memory buffers
        self.tuples = tuples  # number of tuples in one block
        self.tuple_size = tuple_size  # size of each tuple in bytes
        self.left_relation = left_relation  # name of left relation
        self.right_relation = right_relation  # name of right relation

    def phase_one(self):
        left_file_size = os.stat(self.left_relation).st_size
        read_till = self.m * self.tuples * self.tuple_size
        files_to_be_created = math.ceil(left_file_size / read_till)
        print('left size : {a}'.format(a=left_file_size))
        print('files to be created : {a}'.format(a=files_to_be_created))
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

        right_file_size = os.stat(self.right_relation).st_size
        files_to_be_created = math.ceil(right_file_size / read_till)
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

    def read_block(self, which):
        read_data = [] # stores lines
        if which == 'left':
            pass
        else:
            pass


if __name__ == '__main__':
    left_file = sys.argv[1]
    right_file = sys.argv[2]
    memory_buffers = int(sys.argv[3])
    merge_join = MergeJoin(memory_buffers, left_file, right_file, 2, 32)
    merge_join.phase_one()
