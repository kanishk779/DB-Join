#!/bin/bash
java -jar JoinGenerator.jar 3000 4000 3 3 3
g++ -std=c++11 checker.cpp
./a.out $1 $2 outout.txt
python3 main.py $1 $2 $3 $4
#comm -3 <(sort -u outout.txt) <(sort -u inputR_inputS_join.txt)
rm outout.txt
rm $(ls | grep -E "inputR[0-9]+")
rm $(ls | grep -E "inputS[0-9]+")
rm a.out
