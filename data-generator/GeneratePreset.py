### Code started 2021 Feb
### Sample generation for CQAW competition
### run '''python GeneratePreset.py''' 
import numpy as np
from enum import Enum
from collections import Counter 
from time import time
import cv2
import json

from LowLevelFigure import LowLevelFigure
from MidLevelFigure import MidLevelFigure
from HighLevelFigure import HighLevelFigure

# The type of data classes we will be generating
class Dataclass(Enum):
    LENGTH = 0
    LENGTHS = 1
    ANGLE = 2
    ANGLES = 3
    SIMPLE_BAR=4 # simple bar plot, level 2
    SIMPLE_PIE=5 # simple pie plot, level 2
    ADVANCED_BAR=6 # advanced bar plots, level 3
    ADVANCED_PIE=7 # advanced pie plots, level 4

### CHANGE THIS PART FOR DATASET WITH DIFFERENT SIZE
data_counts = {'train':80, 'test':20}
path = './sample_fig/'
prefix = 'SAMPLE_'

# Query matchmaker for advanced bar and pie plots
def advanced_query_matcher(dset):
    # dset is a tuple of training dataset and test dataset

    # The following are the queries
    QUERIES = {
        0: ('What is the value of {X}?', (lambda nums, i, j, k: np.around(nums[i],3))), 
        1: ('Which variety has the maximum value?', (lambda nums, i, j, k: np.argmax(nums) if len(np.atleast_1d(np.argmax(nums)))==1 else None)), 
        2: ('Which variety has the minimum value?', (lambda nums, i, j, k: np.argmin(nums) if len(np.atleast_1d(np.argmin(nums)))==1 else None)), 
        3: ('Is {X} bigger than {Y}?', (lambda nums, i, j, k: 'Yes' if nums[i]>nums[j] else ('No' if nums[i]<nums[j] else None))), 
        4: ('Is {X} smaller than {Y}?', (lambda nums, i, j, k: 'Yes' if nums[i]<nums[j] else ('No' if nums[i]>nums[j] else None))), 
        5: ('Is {X} bigger than the sum of {Y} and {Z}?', (lambda nums, i, j, k: 'Yes' if nums[i]>nums[j]+nums[k] else ('No' if nums[i]<nums[j]+nums[k] else None))), 
        6: ('What is the sum of values for {X} and {Y}?', (lambda nums, i, j, k: np.around(nums[i]+nums[j], 3) ))
    }
    n_queries = len(QUERIES)

    queries = []
    labels = []

    # Randomly matches a query with each nums in dset
    for (_, varieties, nums) in dset:
        while True:
            Q_idx = np.random.randint(n_queries)
            formatQuery, funQuery = QUERIES[Q_idx]
            ints = np.random.choice(len(nums),3,replace=False)
            lab = funQuery(nums, ints[0], ints[1], ints[2])
            if lab is not None: # TODO: do something 
                strQuery = formatQuery.format(X=varieties[ints[0]], Y=varieties[ints[1]], Z=varieties[ints[2]])
                if Q_idx == 1 or Q_idx == 2: 
                    lab = varieties[lab]
                queries = queries + [strQuery]
                labels = labels + [lab]
                break
            else: 
                print("Invalid query for this figure. Choosing a new query...")


    # and testing dataset
    for nums in dset[1]:
        pass
    return queries, labels

def convert(o):
    if isinstance(o, np.int64): return int(o)  
    return o

SIMPLE_QUERIES = ['What is the length of the line in the figure?', 'What are the lengths of the lines in the figure, from left to right?', 
            'What is the size of the angle in the figure?','What are the sizes of the angles in the figure, from left to right?', 
            'What are the values represented in the bar graph, from left to right?', 'What are the values represented in the pie graph, clockwise from the top?']


train_metadata = []
test_metadata = []
admin_metadata = []

for data_class, mem in Dataclass.__members__.items():
    level_switcher = {
        # This dictionary matches each data class with a tuple, 
        # which includes (figure class, level in integer)
        'LENGTH': (LowLevelFigure, 1), 
        'LENGTHS': (LowLevelFigure, 1),
        'ANGLE': (LowLevelFigure, 1), 
        'ANGLES': (LowLevelFigure, 1),
        'SIMPLE_BAR': (MidLevelFigure, 2),
        'SIMPLE_PIE': (MidLevelFigure, 2),
        'ADVANCED_BAR': (HighLevelFigure,3), 
        'ADVANCED_PIE': (HighLevelFigure,3)
    }
    (figure_class, lev) = level_switcher.get(data_class)
    
    (TRAIN_DATA, TEST_DATA) = figure_class.generate_figures(data_class.lower(), counts=(data_counts['train'], data_counts['test']))
    # For high level data, we need to match queries to each figure
    if lev==3:
        (train_queries, train_labels) = advanced_query_matcher(TRAIN_DATA)
        (test_queries, test_labels) = advanced_query_matcher(TEST_DATA)

    # Training dataset
    for i in range(len(TRAIN_DATA)):
        # Exports image files
        td = TRAIN_DATA[i]
        im_filename = prefix+data_class+'_train_'+str(i)+'.png'
        cv2.imwrite(path+im_filename, td[0])
        # Writing metadata
        if lev<3:
            # For lower level data, we directly add to the metadata
            mtdt = {"filename": im_filename, "classtype": data_class.lower(), "level": lev, "query": SIMPLE_QUERIES[mem.value], "label":td[1].tolist()}
        elif lev==3:
            # For higher level data, we match it to the query
            mtdt = {"filename": im_filename, "classtype": data_class.lower(), "level": lev, "query": train_queries[i], 
                "label":train_labels[i]} 
        train_metadata = train_metadata + [mtdt]

    # Testing dataset
    for i in range(len(TEST_DATA)): 
        # Exports image files
        td = TEST_DATA[i]
        im_filename = prefix+data_class+'_test_'+str(i)+'.png'
        cv2.imwrite(path+im_filename, td[0])
        # Writing metadata
        if lev<3:
            # For lower level data, we directly add to the metadata 
            mtdt = {"filename": im_filename, "classtype": data_class.lower(), "level": lev, "query": SIMPLE_QUERIES[mem.value]}
            amtdt = { # Only the admin metadata has the true label
                "filename": im_filename, "classtype": data_class.lower(), "level": lev, "query": SIMPLE_QUERIES[mem.value], 
                "label":td[1].tolist()} 
        elif lev==3:
            # For higher level data, we match it to the query
            mtdt = {"filename": im_filename, "classtype": data_class.lower(), "level": lev, "query": test_queries[i]}
            amtdt = { # Only the admin metadata has the true label
                "filename": im_filename, "classtype": data_class.lower(), "level": lev, "query": test_queries[i], 
                "label":test_labels[i]} 
            # And then add to metadata

        test_metadata = test_metadata + [mtdt]
        admin_metadata = admin_metadata + [amtdt]

    with open('TRAIN_metadata.txt', 'w') as outfile:
        json.dump(train_metadata, outfile, default=convert)
    with open('TEST_metadata.txt', 'w') as outfile:
        json.dump(test_metadata, outfile, default=convert)
    with open('ADMIN_metadata.txt', 'w') as outfile: 
        json.dump(admin_metadata, outfile, default=convert)