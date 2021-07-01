# DB-Join
Iterator for joined relation (DBMS)

This was the project done as part of the Data-Systems course (Advanced DBMS) in
6th semester. Given M blocks of main memory available and two large relations
R(X,Y) and S(Y,Z) the objective is to develop iterators for join of these relations.
There are two ways of joining relations that are used.

#### Join Condition
R.Y == S.Y

## Merge-Sort Join
The first step is to bring the block size chunk of data from relation R(X,Y) and
sort it in memory based on the Y attribute. Then the sorted block is written back to the disk. This way
the whole relation is transformed into a bunch of sorted sub-lists. This is also
done for relation S(Y,Z).
After this we initialize two pointers which point at the beginning, one for each of the relation.
We compare both the tuples pointed by the pointers and take the minimum of the
two. Now if the minimum obtained equals the first tuple of other relation, we
output the join of these two tuples as the next tuple of the JOINED relation.
Else if the minimum is less than the other tuple we advance the pointer for that
relation.
We also need to make sure B(R) + B(S) &lt; M<sup>2</sup> for the initial sorting
to work.

#### Time Complexity
Let us denote by B(R) the number of blocks required to store relation R, by
SZ(R) the size of one tuple of R and T(R) as the number of tuples of R in one
block.
The initial sorting requires B(R)*T(R)*log(T(R)) + B(S)*T(S)*log(T(R)).
After that we need to linearly scan both the relation's sorted sub-lists, which
takes B(R)*T(R) + B(S)*T(S) time.

## Hash Join
The underlying idea is to hash the tuple of relations R and S based on the
attribute Y. Then we are guaranteed to find tuples with same value of Y in the
same bucket of the hash table. So now to generate the tuples of the JOINED
relations we just need to look at one bucket at a time. We maintain a search
structure over the tuples of relation which has lesser number of tuples in that
bucket. Then we iterate over tuples of other relation hashed in that bucket, and
output all the pairs with common value of Y attribute.

#### Hash Function Used
Value of mod is provided by the user, it signifies the number of buckets. A
prime value (Here 31) is considered for the hash function.
```
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
```

## How to run

Usage: 
```
java -jar JoinGenerator.jar noOfrecordsinR noOfrecordsinS sizeofX sizeofY sizeofZ
```
Output: 
Two files will be generated inputR and the inputS column data separated by a single space.
```
python3 main.py PathToR PathToS TypeOfJoin MainMemory
```
