import json
import random
import time
import numpy as np
from deap import algorithms
from deap import base
from deap import creator
from deap import tools


MAX_WEIGHT = 15


class Evaluator(object):
    def __init__(self, items, capacity):
        self.items = items
        self.capacity = capacity

    def __call__(self, candidate):      # Candidate == Rucksack
        total_weight = 0
        total_profit = 0
        item_counter = 0

        # for i in range(len(candidate)):
        #     if candidate[i]:
        #         total_weight += self.items[i]['weight']
        #         total_profit += self.items[i]['profit']

        selectedItemList = []
        selectedItemFlag = False

        # item_idx = random.randint(0, len(candidate) - 1)
        for j in range(len(candidate) - 1):
            selectedItemList.append(candidate[j])
            # print(str(selectedItemList) + "\n")
            total_weight += candidate[j]['weight']
            total_profit += candidate[j]['profit']

            if total_weight > self.capacity:
                break
            elif selectedItemList.count(candidate[j]) > 3:
                selectedItemFlag = True
                break

        if total_weight > self.capacity:
            return 50000, 0                    # Changed: total_weight - self.capacity -> 10000
        elif selectedItemFlag:
            return 20000, 0                     # TODO: Questionable return vals
        else:
            overload = 0

        return overload, total_profit


with open('items2.json') as f:
    items = json.load(f)
    random.shuffle(items)


# with open('capacity2.json') as f:
#     capacity = json.load(f)

capacity = MAX_WEIGHT

evaluator = Evaluator(items, capacity)

# Objectives are decreasing overload and increasing total profit, in that order
creator.create('FitnessMulti', base.Fitness, weights=(-1, 1))               # Changed weight fitness value from -1 to 1.
creator.create('Individual', list, fitness=creator.FitnessMulti)

IND_INIT_SIZE = 5
NBR_ITEMS = 5

toolbox = base.Toolbox()
# toolbox.register('random_bit', lambda: random.choice([False, True]))    # TODO: Problem 'random_bit' - !!!FIXED!!!
# toolbox.register('individual',
#                  tools.initRepeat,
#                  creator.Individual,
#                  toolbox.random_bit,
#                  n = len(items))

def mutList(individual):
    # print(str(individual) + "\n")
    """Mutation function which either adds or pops an element from a list"""
    if random.random() < 0.5:
        if len(individual) > 0:     # Pop-ing an element from an empty list would result in an error.
            # print(str(individual) + "\n")
            removedValue = random.choice(individual)
            individual.remove(removedValue)
        else:
            newValue = random.choice(items)
            individual.append(newValue)

    return individual,


randNumOfItems = random.randint(1, 10)
toolbox.register('random_item', lambda: random.choice(items))
toolbox.register('individual',
                 tools.initRepeat,
                 creator.Individual,
                 toolbox.random_item,
                 n=len(items))

toolbox.register('population', tools.initRepeat, list, toolbox.individual)
toolbox.register('evaluate', evaluator)
toolbox.register('mate', tools.cxTwoPoint)
toolbox.register('mutate', mutList)                # TODO: Problem mutFlipBit -> mutList - !!!FIXED!!!
toolbox.register('select', tools.selBest)         # TODO: Problem selNSGA2 -> selBest ?????????????

# random.seed(42)

NGEN = 1000         # The number of generation.
MU = 50            # The number of individuals to select for the next generation.
LAMBDA = 100        # The number of children to produce at each generation.
CXPB = 0.5          # The probability that an offspring is produced by crossover.
MUTPB = 0         # The probability that an offspring is produced by mutation.


pop = toolbox.population(n=MU)
hof = tools.ParetoFront()

# pop, log = algorithms.eaSimple(pop, toolbox,            # TODO: Problem algorithms.eaSimple -> .eaMuPlusLambda - - !!!FIXED!!!
#                                CXPB,
#                                MUTPB,
#                                NGEN,
#                                halloffame=hof,
#                                verbose=True)

start_time = time.time()
pop, log = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, halloffame=hof, verbose=True)

total_profit = 0
total_weight = 0
best_solution = hof[0]

print('Items selected:')
print(best_solution)

# for i in range(len(best_solution)):               # Best solution calculation was completely wrong.
#     if best_solution[i]:
#         print(i + 1)
#         total_profit += items[i]['profit']
#         total_weight += items[i]['weight']

for i in range(len(best_solution)):
    total_profit += best_solution[i]['profit']
    total_weight += best_solution[i]['weight']

print()
print(f'Total weight: {total_weight}')
print(f'Capacity: {capacity}')
print(f'Total profit: {total_profit}')
print("--- %s seconds ---" % (time.time() - start_time))
