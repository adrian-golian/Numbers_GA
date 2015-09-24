This is an implementation of a genetic algorithm solution to a problem:
"Given an integer, find sequences of numbers and operators such that their result is equal to that integer"

This solution uses 3-bit integers (0 to 7) and operators: +. -. *. /

The potential solutions are stored in binary 'chromosomes'. These binary sequences can be partitioned into 4-bit long 'genes'. Every possible gene sequence is an encoded number or operator.

The program populates the 'zoo' with a number of randomly generated (but valid - to save space) chromosomes. These are then subjected to a darwinian selection process, when they reproduce (no exchange of genes between chromosomes takes place).



HOW-TO:
The basic functionality (give the target integer as an argument): 
		python numbers_operations.py 53

To adjust population size, mutation rates etc. change respective values in the settings in the .py file.



You are free to use this code as you wish.