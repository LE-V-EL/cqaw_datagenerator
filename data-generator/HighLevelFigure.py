### Code started 2021 Feb
import math
from collections import Counter 
import numpy as np
import os
import sys
import cv2
import enum
from time import time

class HighLevelFigure: 
    # Basic parameters for image
    FigSize = (400, 400)
    FigCenter = (200, 200)
    bottomY = 30

    # For bars
    val_min = 32
    val_max = 320
    bar_width = 16
    # For pies
    pie_rad_fixed = 100

    train_vocab = ['PinkLady', 'Empire', 'Fuji', 'Gala', 'Honeycrisp', 'McIntosh', 'Breeze', 'CosmicCrisp', 'Envy', 'Jazz', 'Kiku', 'Opal', 'PacificRose', 'Rome', 'SweeTango']
    test_vocab = ['Valencia', 'Bloody', 'Navel', 'Clementine', 'Tangelo', 'Bitter', 'Bergamot', 'Lima', 'Tangerine', 'Serville', 'Satsuma', 'Maltese', 'Moro', 'Tarocco', 'Hamlin', 'Bahia', 'Washington', 'Jaffa']

    @staticmethod
    def generate_figures(data_class, counts=(8,2)):
        switcher = {
            'advanced_bar' : HighLevelFigure.generate_figure_bar, 
            'advanced_pie' : HighLevelFigure.generate_figure_pie
        }
        figFunc = switcher.get(data_class)

        ### DEPRECATED
        #def check_distribution(nums):
        #    # we dont care until we reach larger amounts
        #    if len(nums) < 1000:
        #        return True
        #    c = Counter(nums)
        #    # not adding anything over 110% of the mean amount in each angle bucket
        #    threshold = np.mean(list(c.values())) * 1.1
        #    for (k, v) in c.items():
        #        if int(v) > threshold:
        #            return False
        #    return True

        total_count = counts[0]+counts[1]
        num_of_numbers = np.random.randint(3, 7, total_count) # How many bars/pies each figure will have
        N = np.sum(num_of_numbers)
        flat = np.repeat(np.arange(HighLevelFigure.val_min,  HighLevelFigure.val_max+1), 
            math.ceil(N/(HighLevelFigure.val_max+1-HighLevelFigure.val_min)+1))
        np.random.shuffle(flat)

        trainNums = []
        testNums = []

        curIdx = 0
        for i in range(counts[0]):
            # Trims the flat array into array of arrays, 
            # FOR TRAINING SET
            trainNums = trainNums + [flat[curIdx:(curIdx+num_of_numbers[i])]]
            curIdx = curIdx+num_of_numbers[i]

        for j in range(counts[0], counts[0]+counts[1]):
            testNums = testNums + [flat[curIdx:(curIdx+num_of_numbers[j])]]
            curIdx = curIdx+num_of_numbers[j]

        return ([figFunc(nums=trainNums[i], testFlag=False) for i in range(counts[0])], 
            [figFunc(nums=testNums[i], testFlag=True) for i in range(counts[1])])

    @staticmethod
    def generate_figure_bar(nums=None, testFlag=False): 
        im = np.ones(HighLevelFigure.FigSize, dtype=np.float32) 
        if nums is None:
            nums = np.random.randint(HighLevelFigure.val_min, HighLevelFigure.val_max+1, size=(6,))
        #else: 
        #    nums = np.array(nums)
        num = len(nums)

        if testFlag: 
            # If test data, take labels from test_vocab
            varieties = np.random.choice(HighLevelFigure.test_vocab, num, replace=False)
            #TODO: we can add variability in color here? 
        else: 
            # Takes labels from train_vocab
            varieties = np.random.choice(HighLevelFigure.train_vocab, num, replace=False)

        # X positions and Y level
        Xs = [int(np.round(HighLevelFigure.FigSize[0]/(num+1)))*(i+1) for i in range(num)]
        Y = HighLevelFigure.FigSize[1] - HighLevelFigure.bottomY
        lineWidth = 1
        barWidth = HighLevelFigure.bar_width

        # Draws rectangles
        for i in range(num):
            cv2.rectangle(im, (Xs[i]-barWidth,Y), (Xs[i]+barWidth,Y-nums[i]), 0, lineWidth)

        # Draws the x-axis at the bottom
        cv2.line(im, (0, Y), (HighLevelFigure.FigSize[0], Y), 0, 1)

        # Puts labels
        for i in range(num):
            text = varieties[i]
            textscale = 0.28
            font = cv2.FONT_HERSHEY_SIMPLEX
            textsize = cv2.getTextSize(text, font, 1, 2)[0] 
            textX = int(np.round(Xs[i] - (textsize[0]*textscale/2)))
            textY = HighLevelFigure.FigSize[1] - int(np.round(HighLevelFigure.bottomY/2))
            cv2.putText(im, text, (textX, textY), font, textscale, 0)

        # Adds noise and normalizes
        noise = np.random.uniform(0, 0.05, HighLevelFigure.FigSize)
        im += noise

        # TODO: comment this later
        #tempText = np.array2string(nums)
        #tempText2 = np.array2string(varieties)
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.putText(im, tempText, (150, 15), font, 0.4, 0.3)
        #cv2.putText(im, tempText2, (50, 25), font, 0.4, 0.3)
        # TODO: uncomment this part when you are going to save the figure instead of showing
        im = im*255.0
        im = np.minimum(im, 255.0)
        im = np.maximum(im, 0.0)

        assert len(nums) > 2
        # Returns the figure and true labels
        return (im, varieties, nums)

    @staticmethod
    def generate_figure_pie(nums=None, testFlag=False):
        im = np.ones(HighLevelFigure.FigSize, dtype=np.float32) 
        if nums is None:
            nums = np.random.randint(HighLevelFigure.val_min, HighLevelFigure.val_max+1, size=(6,))
        #else: 
        #    nums = np.array(nums)
        nums = nums/np.sum(nums)
        nums = np.around(nums, 3)
        num = len(nums)

        if testFlag: 
            # If test data, take labels from test_vocab
            varieties = np.random.choice(HighLevelFigure.test_vocab, num, replace=False)
            #TODO: we can add variability in color here? 
        else: 
            # Takes labels from train_vocab
            varieties = np.random.choice(HighLevelFigure.train_vocab, num, replace=False)
        lineWidth = 3
        X = HighLevelFigure.FigCenter[0]
        Y = HighLevelFigure.FigCenter[1]
        r = HighLevelFigure.pie_rad_fixed
        # Draws circle
        cv2.ellipse(im, (X, Y), (r, r), 0, 0, 360, 0, lineWidth)

        # Partitions each 'pie' and labels them with the apple/orange varieties
        HAFP = int(np.round(nums[0]*360/2)) # Half the Angle of First Pie, used temporarily
        QAFP = int(np.round(nums[0]*360/4)) # Quarter the Angle of First Pie, used temporarily
        first_line_dir = np.random.randint(90-HAFP-QAFP, 90-QAFP) # TODO: do something about this
        theta = (np.pi / 180.0) * first_line_dir
        END = (X - r*np.cos(theta), Y - r*np.sin(theta))
        cv2.line(im, (X,Y), (int(np.round(END[0])), int(np.round(END[1]))), 0, lineWidth)
        for i in range(num-1):
            second_line_dir = first_line_dir+(360*nums[i]) # Direction of two lines in an angle
            # draws first line            
            theta = (np.pi / 180.0) * second_line_dir
            END = (X - r*np.cos(theta), Y - r*np.sin(theta))
            cv2.line(im, (X,Y), (int(np.round(END[0])), int(np.round(END[1]))), 0, lineWidth)

            mid_text_dir = (first_line_dir+second_line_dir)/2
            text = varieties[i]
            textscale = 0.28
            font = cv2.FONT_HERSHEY_SIMPLEX
            textsize = cv2.getTextSize(text, font, 1, 2)[0] 
            textX = X - (r+30)*np.cos((np.pi / 180.0) * mid_text_dir)
            textY = Y - (r+30)*np.sin((np.pi / 180.0) * mid_text_dir)
            textX = int(np.round(textX - (textsize[0]*textscale/2))) # center the textbox again
            textY = int(np.round(textY - (textsize[1]*textscale/2)))
            cv2.putText(im, text, (textX, textY), font, textscale, 0)

            # Updates first line dir
            first_line_dir = second_line_dir

        # Adds the last variety name
        second_line_dir = first_line_dir+(360*nums[num-1])
        mid_text_dir = (first_line_dir+second_line_dir)/2
        text = varieties[num-1]
        textscale = 0.28
        font = cv2.FONT_HERSHEY_SIMPLEX
        textsize = cv2.getTextSize(text, font, 1, 2)[0] 
        textX = X - (r+30)*np.cos((np.pi / 180.0) * mid_text_dir)
        textY = Y - (r+30)*np.sin((np.pi / 180.0) * mid_text_dir)
        textX = int(np.round(textX - (textsize[0]*textscale/2))) # center the textbox again
        textY = int(np.round(textY - (textsize[1]*textscale/2)))
        cv2.putText(im, text, (textX, textY), font, textscale, 0)

        # TODO: comment this later
        #tempText = np.array2string(nums)
        #tempText2 = np.array2string(varieties)
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.putText(im, tempText, (150, 15), font, 0.4, 0.3)
        #cv2.putText(im, tempText2, (50, 25), font, 0.4, 0.3)
        
        # Adds noise and normalizes
        noise = np.random.uniform(0, 0.05, im.shape)
        im += noise
        # TODO: uncomment this part when you are going to save the figure instead of showing
        im = im*255.0
        m = np.minimum(im, 255.0)
        im = np.maximum(im, 0.0)

        # Returns the figure and true labels
        return (im, varieties, nums)



#(im, varieties, angleSize) = HighLevelFigure.generate_figure_pie(testFlag=True)
#print(angleSize)
#cv2.imshow("Testing angle",im)
#cv2.waitKey(0)
#cv2.imwrite('testtest.png', im)
