import numpy as np
import copy 
import pandas as pd
from problem_model import problem


p = problem.problem()

p.input("eg1.txt")

p.make_graphs()

print(p)

print(p.theoritical_minima())

