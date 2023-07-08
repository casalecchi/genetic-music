from random import choices, randint, randrange, random, sample
from typing import List, Callable, Optional, Tuple

Genome = List[int]
Population = List[Genome]
PopulationFunc = Callable[[int, int], Population]
FitnessFunc = Callable[[Genome], int]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]
PrinterFunc = Callable[[Population, int, FitnessFunc], None]


def generate_genome(length: int) -> Genome:
    return choices([0, 1], k=length)


def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]


def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes must have same length")
    
    length = len(a)
    point = randint(1, length - 1)

    if length > 2:
        a = a[:point] + b[point:]
        b = b[:point] + a[point:]

    return a, b


def mutation(genome: Genome, num_mutations: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num_mutations):
        index = randrange(len(genome))
        
        if random() < probability:
            abs(genome[index] - 1)
    
    return genome


def population_fitness(population: Population, fitness_func: FitnessFunc) -> int:
    return sum([fitness_func(genome) for genome in population])


def generate_weighted_distribution(population: Population, fitness_func: FitnessFunc) -> Population:
    """Return a new population containing genomes from given population based on their scores"""

    result = []

    for genome in population:
        result += [genome] * int(fitness_func(genome)+1)

    return result


def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    """Pick two genomes with the probability based on their scores"""
    population = generate_weighted_distribution(population, fitness_func)
    
    return sample(population, k=2)


def sort_population(population: Population, fitness_func: FitnessFunc) -> Population:
    return sorted(population, key=fitness_func, reverse=True)


def genome_to_string(genome: Genome) -> str:
    return "".join(map(str, genome))


def print_stats(population: Population, generation_id: int, fitness_func: FitnessFunc):
    print("GENERATION %10d" % generation_id)
    print("=============")
    print("Population: [%s]" % ", ".join([genome_to_string(gene) for gene in population]))
    print("Avg. Fitness: %f" % (population_fitness(population, fitness_func) / len(population)))
    sorted_population = sort_population(population, fitness_func)
    print(
        "Best: %s (%f)" % (genome_to_string(sorted_population[0]), fitness_func(sorted_population[0])))
    print("Worst: %s (%f)" % (genome_to_string(sorted_population[-1]),
                              fitness_func(sorted_population[-1])))
    print("")

    return sorted_population[0]


def run_evolution(
        population_func: PopulationFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 100,
        printer: Optional[PrinterFunc] = None) -> Tuple[Population, int]:
    
    population = population_func(10, 10)

    # i = 0
    # while True:
    for i in range(generation_limit):
        population = sort_population(population, fitness_func)

        if printer is not None:
            printer(population, i, fitness_func)
        
        if fitness_func(population[0]) >= fitness_limit:
            break

        # Elitism - Pick the best 2 genomes of previous population
        next_generation = population[0:2]

        for _ in range(int(len(population) / 2) - 1):
            parents = selection_func(population, fitness_func)
            a, b = crossover_func(parents[0], parents[1])
            a = mutation_func(a)
            b = mutation_func(b)
            next_generation += [a, b]

        population = next_generation

        i += 1

    return population, i
