import csv
import time
import pandas
#import numpy as np
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

class pitchfork_analysys():
    def __init__(self, file):

        # pandas
        self.file = file
        data = pandas.read_csv(file, header=0)
        self.print_()
        print(data.info())
        self.print_()
        print(data.describe())
        self.print_()
        print('Best ratings:')
        print(data[['﻿Artist', 'Genre', 'Year', 'Ratings']][data['Ratings'] > 9.6])
        self.print_()

        # sklearn
        '''
        data_params = np.array(data.values[:,4:6], dtype='float64')
        data_params = scale(data_params)
        X = PCA(n_components=2).fit_transform(data_params)
        data_num = X.shape[0]

        OUTLIER_FRACTION = 0.01
        clf = svm.OneClassSVM(kernel='rbf')
        clf.fit(X)
        dist_to_border = clf.decision_function(X).ravel()

        threshold = stats.scoreatpercentile(dist_to_border, 100 * OUTLIER_FRACTION)
        is_inlier = dist_to_border > threshold
        xx, yy = np.meshgrid(np.linspace(-7, 7, 500), np.linspace(-7, 7, 500))
        n_inliers = int((1. - OUTLIER_FRACTION) * data_num)
        n_outliers = int(OUTLIER_FRACTION * data_num)
        Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        plt.title("Outlier Detection")
        plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), threshold, 7), cmap=plt.cm.Blues_r)
        a = plt.contour(xx, yy, Z, levels=[threshold], linewidths=2, colors='red')
        plt.contourf(xx, yy, Z, levels=[threshold, Z.max()], colors='white')
        b = plt.scatter(X[is_inlier == 0, 0], X[is_inlier == 0, 1], c='red')
        c = plt.scatter(X[is_inlier == 1, 0], X[is_inlier == 1, 1], c='green')
        plt.axis('tight')
        plt.legend([a.collections[0], b, c], ['decision function', 'outliers', 'inliers'],
                   prop=matplotlib.font_manager.FontProperties(size=14))
        plt.xlim((-7, 7))
        plt.ylim((-7, 7))
        plt.show()
        '''
        # PIVOT TABLE
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
        print('Ratings on years:')
        print(pivot_year)

    def print_(self):
        print('_______________________________________________________________________________ \n')

if __name__ == '__main__':
    time_start = time.time()
    file = 'pytch.csv'
    data = pitchfork_analysys(file)
    data_end = float(format(time.time() - time_start))
    print('Process finished at', round(data_end, 3), 's.')
