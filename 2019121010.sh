java -jar JoinGenerator.jar 660 700 3 3 3
g++ -std=c++11 checker.cpp
./a.out inputR inputS outout.txt
sort -u outout.txt > temp1.txt 
touch output.txt
python3 main.py inputR inputS sort 25
sort -u output.txt > temp2.txt
comm -3 temp1.txt temp2.txt
rm output.txt
rm outout.txt
rm $(ls | grep -E "input.{2}")
rm a.out
