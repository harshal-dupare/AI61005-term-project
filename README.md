# AIFA

![image](https://user-images.githubusercontent.com/52428908/111369680-5cdf2180-86bd-11eb-9d33-0f51f32ee6ab.png)

### Download

* Download the repository

### Setup

* Install all the packages in `requirements.txt`
* Python version 3 and above 

### Run the following in `src` to generate a random test case

```
python generator.py
````

then a randomly generated example will be written to `gen_testcase.txt`, not that this testcase has a solution, which is guaranteed by the `generator.py`

### Run the algorithm of the generated test case

```
python ctr.py
python ctmr.py
```

Note: `ctr.py` & `ctmr.py` assumes that the input in `gen_testcase.txt` has a solution 

### Example

```
C:\Users\harshal d\Desktop\AIFA\src>python generator.py
Graph Completed
Source destination and params completed
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 4999.17it/s]
Max weight Completed
```

```
C:\Users\harshal d\Desktop\AIFA\src>python ctr.py       
Lower bound is:  32.4756941358828 

output of algoritm is:  32.4756941358828

Paths that are followed are:

for EV 0 : [(23.09028995352622, 'reached without charging at destination on path [2, 12, 10, 1]')]
for EV 1 : [(0, 'started charging at 11'), (9.569532843208096, 'completed charging at 11'), (22.69900776174788, 'reached 14'), (32.4756941358828, 'reached destination on path [14, 15]')]       
for EV 2 : [(6.09021668782382, 'reached without charging at destination on path [4, 10, 12, 3]')]
for EV 3 : [(0, 'started charging at 9'), (1.9240183812064784, 'completed charging at 9'), (5.693166485135418, 'reached 13'), (11.478115774784175, 'reached destination on path [13, 14, 7, 0]')]
for EV 4 : [(3.6185751533339374, 'reached without charging at destination on path [7, 12, 3]')]a
```