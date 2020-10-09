#!/Users/vk/miniconda3/bin/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import time
import warnings
warnings.filterwarnings('ignore')
import pickle

from sklearn import model_selection
from sklearn import metrics
import seaborn as sns

modelFolder = '/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/models/ORIGINAL/'
data = pd.read_csv('/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/data/StockTrainData.csv')

features = ['high', 'low', 'average', 'volume', 'numberOfTrades', 'open',  'close', 'momentum_roc', 
            'momentum_rsi', 'momentum_stoch', 'trend_macd']


# Separating out the features
rollingData = data.filter(features)

rollingData = rollingData.fillna(method='ffill')
rollingDataDiff = rollingData.pct_change()
rollingDataDiff.replace([np.inf, -np.inf, np.nan], 0.000001,inplace=True)
tr_close = rollingDataDiff['close']
tr_direction = (tr_close > tr_close.shift()).astype(int)
rollingDataDiff['target'] = tr_direction.shift(-1).fillna(0).astype(int)

X = rollingDataDiff.iloc[:,:-1]
y = rollingDataDiff['target']

x_train, x_test, y_train, y_test = model_selection.train_test_split(X, y, train_size=0.70,test_size=0.30, random_state=21)



# SVC

from sklearn import svm

svmClassifier = svm.SVC()

svmFit = svmClassifier.fit(x_train, y_train)

svmPredictions = svmClassifier.predict(x_test)



# get the accuracy
accScore = accuracy_score(y_test, svmPredictions)
print (accScore)


# SVM confusion matrix
'''

cm = metrics.confusion_matrix(y_test, svmPredictions)
plt.figure(figsize=(9,9))
sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True, cmap = 'Blues_r');
plt.ylabel('Actual label');
plt.xlabel('Predicted label');
all_sample_title = 'Accuracy Score: {0}'.format(accScore)
plt.title(all_sample_title, size = 15);
'''


# load the model


model_name = 'SVM'
model_file = str(modelFolder) + str(model_name) + '.pkl'
pickle.dump(svmFit, open(model_file, 'wb'))


