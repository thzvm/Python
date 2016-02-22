import csv
import time
import pandas
import numpy as np
#import matplotlib.pylab as plt
#import matplotlib.font_manager
#import scipy.stats as stats
#from sklearn import svm
#from sklearn.preprocessing import scale
#from sklearn.decomposition import PCA



class pitchfork_excel():
    ''''''
    def __init__(self, file):
        ''''''
        self.data = []
        with open(file, newline='') as pitchfork:
            data_read = csv.reader(pitchfork, delimiter=';')
            for line in data_read:
                self.data.append(tuple(line))
            print(len(self.data))
            data_dict_array = []
            for n in range(len(self.data)):
                data_dict = {}
                for i in range(len(self.data[1])-1):
                    data_dict[self.data[0][i]] = self.data[n][i]
                    try:
                        if self.data[n][2]:
                            int(self.data[n][2])
                            self.error = False
                    except ValueError:
                        self.error = True

                if self.error == True:
                    data_dict_array.append(data_dict)

            self.rat_average(data_dict_array)

    def rat_average(self, array):
        """Average rating & """
        data_dict_array = array
        ratings = 0
        for i in range(len(data_dict_array)):
            ratings += float(data_dict_array[i]['Ratings'].replace(',','.'))
            print(data_dict_array[i]['Ratings'])
        print(round(ratings / len(data_dict_array), 3))
        print(len(data_dict_array))

class pitchfork_analysys():
    def __init__(self, file):
        self.file = file
        data = pandas.read_csv(file, header=0)
        self.print_()
        print(data.info())
        self.print_()
        print(data.describe())
        self.print_()

        self.print_()
        print('Best ratings:')
        print(data[['﻿Artist', 'Genre', 'Year', 'Ratings']][data['Ratings'] > 9.9])
        self.print_()
        #data_params = np.array(data.values[:,5:6], dtype='float64')
        '''
        Function	Description
        count	Number of non-null observations
        sum	Sum of values
        mean	Mean of values
        mad	Mean absolute deviation
        median	Arithmetic median of values
        min	Minimum
        max	Maximum
        mode	Mode
        abs	Absolute Value
        prod	Product of values
        std	Unbiased standard deviation
        var	Unbiased variance
        sem	Unbiased standard error of the mean
        skew	Unbiased skewness (3rd moment)
        kurt	Unbiased kurtosis (4th moment)
        quantile	Sample quantile (value at %)
        cumsum	Cumulative sum
        cumprod	Cumulative product
        cummax	Cumulative maximum
        cummin	Cumulative minimum
        '''

        pivot_year = data.pivot_table(['Ratings'], ['Year'], aggfunc='count', fill_value = 0)
        #pivot_year = data.pivot(index='Year', columns='Genre', values='Ratings')
        print('Ratings on years:')
        print(pivot_year)
    def print_(self):
        print('_______________________________________________________________________________ \n')

if __name__ == '__main__':
    time_start = time.time()
    file = 'pytch.csv'
    #data = pitchfork_excel(file)
    data = pitchfork_analysys(file)
    data_end = float(format(time.time() - time_start))
    print('Process finished at', round(data_end, 3), 's.')



