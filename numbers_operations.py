#Copyright 2015 Adrian Golian
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.



import sys
from random import randint, random
from math import exp, sqrt, log
from collections import OrderedDict, Counter

def rand_seq(n = 12):
	sequence = []
	for x in xrange(n):
		sequence.append(repr(randint(0,1)))
	return ''.join(sequence)


class CustomException(Exception):
	pass


class Gene:
	"""A gene class - a four digit long, binary gene"""
	def __init__(self, sequence):
		if len(sequence) == 4:
			self.sequence = sequence
		else:
			raise CustomException("Gene: '"+sequence+"' is not length 4")
		self.feature, self.gene_type = self._decode_seq()

	features = {
		'1000' : '+',
		'1001' : '-',
		'1010' : '*',
		'1011' : '/',
		'1100' : '+',
		'1101' : '-',
		'1110' : '*',
		'1111' : '/'
		}

	#Decode the gene's feature and type
	def _decode_seq(self):
		feature = int(self.sequence, 2) if int(self.sequence, 2) < 8 else self.features[self.sequence]
		if isinstance(feature, str):
			if feature == 'N':
				gene_type = 'N'
			else:
				gene_type = 'operator'
		elif isinstance(feature, int):
			gene_type = 'number'
		return str(feature), gene_type


class Chromosome:
	"""A chromosome class - a variable length, binary chromosome"""
	def __init__(self, sequence, old_age=5):
		self.sequence = sequence[:(len(sequence)/4)*4]        #cut a piece of length n, n%4=0
		self.genes = self._partition_genes()
		self.age = 0
		self.alive = True
		self.old_age = old_age

	def _partition_genes(self):
		if isinstance(self.sequence, str):
			gene_codes =  [self.sequence[i:i+4] for i in range(0, len(self.sequence), 4)]
			return [Gene(code) for code in gene_codes]
		if isinstance(self.sequence, list):
			for gene in self.sequence:
				if len(gene) != 4:
					raise TypeError("Chromosome not a string or a valid list")
			else:
				return self.sequence

	def result(self):
		try:
			return eval(' '.join([gene.feature for gene in self.genes]))
		except:
			return 'N'

	def result_formula(self):
		return ' '.join([gene.feature for gene in self.genes])

	def fitness(self, target_number):
		if isinstance(self.result(), int):
			return exp(-sqrt(abs(target_number-self.result())/float(abs(target_number))))
		else:
			return 0

	def aging(self):
		self.age += 1
		if self.age >= self.old_age:
			self.alive = False

	def reproduce(self, mutation_rate=0.0001):
		new_sequence = ""
		#Create a mutated offspring sequence
		for n in xrange(len(self.sequence)):
			if random() < mutation_rate:
				new_sequence += str( 1-int(self.sequence[n]) )
			else:
				new_sequence += self.sequence[n]
		return Chromosome(new_sequence, self.old_age)




#Populate the zoo
def populate_zoo(target_number, init_pupulation_size):
	zoo = {}
	init_chromosome_length = (3*int(log(target_number, 7))+2)*4
	if (init_chromosome_length/4) % 2 == 0:
		init_chromosome_length -= 4
	for n in xrange(init_pupulation_size):
		done = False
		while not done:                                               #Generate valid (live) chromosomes only
			animal = Chromosome(rand_seq(init_chromosome_length))
			if animal.fitness(target_number) != 0:
				done = True
		try:
			animal.old_age = 5/(1-animal.fitness(target_number))      #Let the strong ones live longer
		except:
			pass
		zoo[repr(n)] = animal                                         #Put the animal in the zoo
		if zoo[repr(n)].fitness(target_number) == 1:
			print zoo[repr(n)].result(), zoo[repr(n)].result_formula()
	return zoo

#Advance the population in time (+ 1 generation)
#Darwinian selection takes place in this function (during reproduction)
def next_generation(zoo, target_number, pupulation_size, minimum_fitness, mutation_rate, offspring_count):
	for m in xrange(pupulation_size):

		try:                                                                                   #Grab a potential parent from the zoo
			animal = zoo[repr(m)]
			if animal.fitness(target_number) != 1:
				zoo[repr(m)].aging()
			if animal.fitness(target_number) < minimum_fitness:
				zoo[repr(m)].alive = False
		except KeyError:
			continue

		if animal.alive:
			for n in xrange(int(animal.fitness(target_number)**2 * offspring_count)):          #Let the strong ones reproduce more
				offspring = animal.reproduce(mutation_rate)
				try:
					offspring.old_age = 5/(1-offspring.fitness(target_number))
				except:
					pass
				if offspring.fitness(target_number) != 0:                                      #Put live offspring in the zoo
					zoo[repr(pupulation_size+m)] = offspring
		if animal.fitness(target_number) >= 1:
			print animal.result(), animal.result_formula()
	if pupulation_size == len(zoo):
		print "Population terminated"
	return zoo





"""---------------------------------------------------------"""




"""Run the GA"""
#SETTINGS:
target_number = 42 if len(sys.argv) == 1 else int(sys.argv[1])
init_pupulation_size = 5000
maximum_population = 50000
mutation_rate = 0.05
minimum_fitness = 0.6
offspring_count = 300
number_of_generations = 5

#Populate 
zoo = populate_zoo(target_number, init_pupulation_size)
minimum_fitness = 0.6 * max([cage[1].fitness(target_number) for cage in zoo.items()])

#Automatically progress generations
for i in xrange(number_of_generations-1):
	print "GENERATION ", i+1, "POPULATION SIZE: ", len(zoo)
	if len(zoo) > maximum_population:
		break
	zoo = next_generation(zoo, target_number, len(zoo), minimum_fitness, mutation_rate, offspring_count)

#Ask for permission to run more generations
done = False
while not done:
	i += 1
	if raw_input("Next generation?  (y/n)     ") == "y":
		print "GENERATION ", i+1, "POPULATION SIZE: ", len(zoo)
		zoo = next_generation(zoo, target_number, len(zoo), minimum_fitness, mutation_rate, offspring_count)
	else:
		done = True


#When experiment is done:

darwinned_animals = OrderedDict(sorted(list({cage[0] : cage[1].fitness(target_number) for cage in zoo.items()}.items()) , key = lambda tup: tup[1], reverse = False))

#Find best performers
final_solutions = []
print "SOLUTIONS FOUND:"
done = False
threshold = 1
while not done:
	cage, fitness = darwinned_animals.popitem(last = True)
	if fitness >= threshold:
		final_solutions.append(zoo[cage].result_formula())
	elif len(final_solutions) == 0:
		print "NONE. BEST PERFORMERS FOUND:"
		threshold = 0.8
		if fitness >= threshold:
			final_solutions.append(zoo[cage].result_formula())
	else:
		done = True

counts = Counter(final_solutions)
for element in list(OrderedDict.fromkeys(final_solutions)):
	print eval(element), element, "    ", counts[element]
