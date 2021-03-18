java -jar JoinGenerator.jar 100 100 15 15 15
g++ -std=c++11 checker.cpp
./a.out inputR inputS outout.txt
sort -u outout.txt > outout.txt 
rm input*
rm a.out
