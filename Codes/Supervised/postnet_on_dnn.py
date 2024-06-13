# -*- coding: utf-8 -*-
"""PostNet on DNN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NgChdZiAjEcXJpY0k8a2YzUAnpTg7BRd
"""

# from google.colab import drive
# drive.mount('/content/drive')

# Import section
import os
import keras
import scipy.io
import statistics
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import optimizers
from keras import backend as K
from collections import Counter
from keras.optimizers import Adam
from keras.models import Sequential
from sklearn.metrics import f1_score
from keras.utils import to_categorical
from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import ModelCheckpoint ,EarlyStopping
from keras.layers import TimeDistributed, Dense, Dropout, BatchNormalization, Dropout, Masking

#loading data

def dl(path):
  data = scipy.io.loadmat(path)
  print(data.keys())
  x = data['features']; y = data['labels'];
  if 'test' in path and 'TDNN' in path:
    w = data['w']
    test_ind = data['test_ind']
    return x, y, w, test_ind
  elif 'test' in path and 'TDNN' not in path:
    w = data['w']
    return x, y, w
  else:
    return x, y.T

def convert_function(arr):
  temp=[]
  for i in arr:
    if i>0.5:
      temp.append(1)
    else:
      temp.append(0)
  return temp

def calculate_accuracy(arr1, arr2):
  count=0
  for itr1, itr2 in zip(arr1, arr2):
    if itr1==itr2:
      count+=1
  return count/len(arr1)

def make_partitions(arr_words, arr_labels):
  v=[]
  np.array(v)
  temp=[]
  for i in range(len(arr_words)-1):
    word=arr_words[i]
    next_word=arr_words[i+1]
    temp.append(arr_labels[i][0])
    if word!=next_word:
      numpy_temp=np.array(temp)
      temp_max=np.amax(numpy_temp)
      numpy_temp=np.divide(numpy_temp, temp_max)
      v=np.concatenate((v, numpy_temp), axis=None)
      temp.clear()
    if (i==len(arr_words)-2):
      temp.append(arr_labels[i+1][0])
      numpy_temp=np.array(temp)
      temp_max=np.amax(numpy_temp)
      numpy_temp=np.divide(numpy_temp, temp_max)
      v=np.concatenate((v, numpy_temp), axis=None)
      temp.clear()
  v1=[]
  for i in v:
    if i==1:
      v1.append(1)
    else:
      v1.append(0)
  return v1


def make_partitions2(arr_words, arr_labels):
  v=[]
  np.array(v)
  temp=[]
  for i in range(len(arr_words)-1):
    word=arr_words[i]
    next_word=arr_words[i+1]
    temp.append(arr_labels[i])
    if word!=next_word:
      numpy_temp=np.array(temp)
      temp_max=np.amax(numpy_temp)
      numpy_temp=np.divide(numpy_temp, temp_max)
      v=np.concatenate((v, numpy_temp), axis=None)
      temp.clear()
    if (i==len(arr_words)-2):
      temp.append(arr_labels[i+1])
      numpy_temp=np.array(temp)
      temp_max=np.amax(numpy_temp)
      numpy_temp=np.divide(numpy_temp, temp_max)
      v=np.concatenate((v, numpy_temp), axis=None)
      temp.clear()
  v1=[]
  for i in v:
    if i==1:
      v1.append(1)
    else:
      v1.append(0)
  return v1

def sampling(args):
    z_mean, z_log_sigma = args
    epsilon = K.random_normal(shape=(K.shape(z_mean)[0], latent_dim), mean=0., stddev=0.004)
    return z_mean + K.exp(z_log_sigma) * epsilon

def normalization(feats,avg,std):
  ii=0
  for v in feats:
    # print(len(v))
    feats[ii] = np.divide((v-avg),std)
    ii = ii+1
  return feats

filee = 'GER_AC_features_TDNN.mat'

print('Classification with::::::',os.path.basename(filee))

train_path = filee;
xtrain1, ytrain1 = dl(train_path);

train_size = xtrain1.shape[0]
print(train_size)

avg_trainfeat1=np.mean(xtrain1, axis=0)
std_trainfeat1=np.std(xtrain1, axis=0)

test_path = 'GER_test_AC_features.mat'
print('test file:::::::',os.path.basename(test_path))

xtest1, ytest1, wtest1 = dl(test_path);

xtest_ac = normalization(xtest1,avg_trainfeat1,std_trainfeat1)

xtrain1 = normalization(xtrain1,avg_trainfeat1,std_trainfeat1)
print(xtrain1.shape)

woPP=[]; wPP=[]
accuracy_all_folds_wopp = []; accuracy_all_folds_wpp = []; f1score_all_folds_wopp = []; f1score_all_folds_wpp = [];
accuracy_all_folds_wopp_a = [];  accuracy_all_folds_wpp_a  = [];  f1score_all_folds_wopp_a  = [];  f1score_all_folds_wpp_a  = [];


print(xtrain1.shape)
print(ytrain1.shape)

highest_accuracy = 0.0

# for j in range(0,1): # folds - change it to 5 folds with complete data

#   xval_ac = xtrain1[(train_size*j)//5:(train_size*(j+1))//5];
#   print(xval_ac.shape)
#   yval_ac = ytrain1[(train_size*j)//5:(train_size*(j+1))//5]
#   xtra_ac = np.concatenate((xtrain1[:(train_size*j)//5], xtrain1[((train_size*(j+1))//5):]), axis=0);
#   ytra_ac = np.concatenate((ytrain1[:(train_size*j)//5], ytrain1[((train_size*(j+1))//5):]), axis=0)

#   # model
#   model = Sequential()
#   model.add(Dense(64, input_shape=(38,), activation='relu'))
#   model.add(BatchNormalization())
#   model.add(Dropout(0.3))
#   model.add(Dense(32, activation='relu'))
#   model.add(BatchNormalization())
#   model.add(Dropout(0.2))
#   model.add(Dense(16, activation='relu'))
#   model.add(Dense(4, activation='relu'))
#   model.add(Dense(1, activation='sigmoid', name='stress'))

#   model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

#   model.fit(xtra_ac, ytra_ac , epochs=200, batch_size=25
#           , validation_data=(xval_ac,yval_ac)
#           , callbacks=[EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=5)]
#           )

#   accuracy = model.evaluate(xtest_ac,ytest1)[1]
#   pred_output= model.predict(xtest_ac)
#   pred_output_a= pred_output
#   y_pred_a = np.where(pred_output_a > 0.5, 1, 0)
#   post_labels=make_partitions(wtest1, pred_output)
#   accuracy_xtest_a=calculate_accuracy(post_labels, ytest1)

#   # for saving the model weights for loading to TDNN
#   if accuracy > highest_accuracy:
#         highest_accuracy = accuracy

#         # Save the model weights after achieving a new highest accuracy
#         model.save_weights('best_model_weights.h5')

#   F1_score_WoPP_a = f1_score(ytest1, y_pred_a)
#   F1_score_WPP_a = f1_score(ytest1, post_labels)

#   accuracy_all_folds_wopp_a.append(round(accuracy * 100, 3))
#   accuracy_all_folds_wpp_a.append(round(accuracy_xtest_a * 100, 3))
#   f1score_all_folds_wopp_a.append(round(F1_score_WoPP_a * 100, 3))
#   f1score_all_folds_wpp_a.append(round(F1_score_WPP_a * 100, 3))

# print(accuracy_all_folds_wopp_a)
# '''average1 = statistics.mean(accuracy_all_folds_wopp_a)
# std1 = statistics.stdev(accuracy_all_folds_wopp_a)
# print("Average:", average1)
# print("Standard Deviation:", std1)'''

# print(accuracy_all_folds_wpp_a)
# '''average2 = statistics.mean(accuracy_all_folds_wpp_a)
# std2 = statistics.stdev(accuracy_all_folds_wpp_a)
# print("Average:", average2)
# print("Standard Deviation:", std2)'''

# print(f1score_all_folds_wopp_a)
# '''average3 = statistics.mean(f1score_all_folds_wopp_a)
# std3 = statistics.stdev(f1score_all_folds_wopp_a)
# print("Average:", average3)
# print("Standard Deviation:", std3)'''

# print(f1score_all_folds_wpp_a)
# '''average4 = statistics.mean(f1score_all_folds_wpp_a)
# std4 = statistics.stdev(f1score_all_folds_wpp_a)
# print("Average:", average4)
# print("Standard Deviation:", std4)'''

xtrain1, ytrain1 = dl("GER_AC_features_TDNN.mat")
xtest_ac, ytest, wtest, test_ind = dl("GER_test_AC_features_TDNN.mat")
xt, yt, wt = dl("GER_test_AC_features.mat")

print("TDNN train data features:", xtrain1.shape, "\nTDNN train data labels:", ytrain1.shape)
print("TDNN test data features:", xtest_ac.shape, "\nTDNN test data labels: ",ytest.shape, "\nTDNN test data syllable count: ",wtest.shape, "\nDNN test data features: ",xt.shape, "\nDNN test data labels: ",yt.shape, "\nDNN test data word count: ", wt.shape)

yt = yt.flatten()
wtest = wtest.flatten()
test_ind = test_ind.flatten()
print(yt.shape, wtest.shape, test_ind.shape)

original_dim = 38

woPP = []
wPP = []
accuracy_all_folds_wopp_a = []
accuracy_all_folds_wpp_a = []
f1score_all_folds_wopp_a = []
f1score_all_folds_wpp_a = []
accuracy_all_folds_wpp_a1 = []
j=0

train_size = xtrain1.shape[0]
ytrain1 = ytrain1.flatten()

for j in range(0,1): # folds

  xval_ac = xtrain1[(train_size*j)//5:(train_size*(j+1))//5];
  print(xval_ac.shape)
  yval_ac = ytrain1[(train_size*j)//5:(train_size*(j+1))//5]
  xtra_ac = np.concatenate((xtrain1[:(train_size*j)//5], xtrain1[((train_size*(j+1))//5):]), axis=0);
  ytra_ac = np.concatenate((ytrain1[:(train_size*j)//5], ytrain1[((train_size*(j+1))//5):]), axis=0)


  print("hi",xtra_ac.shape, xval_ac.shape)

  max_sequence_length = 5
  print(f"\nFold {j + 1} - Max Sequence Length: {max_sequence_length}")

  model1 = Sequential()
  model1.add(Masking(mask_value=-1, input_shape=(max_sequence_length, original_dim)))
  model1.add(TimeDistributed(Dense(64, activation='relu')))
  model1.add(TimeDistributed(BatchNormalization()))
  model1.add(TimeDistributed(Dropout(0.3)))
  model1.add(TimeDistributed(Dense(32, activation='relu')))
  model1.add(TimeDistributed(BatchNormalization()))
  model1.add(TimeDistributed(Dropout(0.2)))
  model1.add(TimeDistributed(Dense(16, activation='relu')))
  model1.add(TimeDistributed(Dense(4, activation='relu')))
  model1.add(TimeDistributed(Dense(1, activation='sigmoid', name='stress')))

  model1.load_weights('DNN_weights.h5')

  model1.compile(optimizer=Adam(learning_rate=0.005), loss='binary_crossentropy', metrics=['accuracy'])


  sequence_length = 5
  num_sequences = len(xtra_ac) // sequence_length

  xtra_ac_reshaped = xtra_ac[:num_sequences * sequence_length].reshape((num_sequences, sequence_length, 38))
  print(xtra_ac_reshaped.shape)

  ytra_ac_modified = np.zeros((num_sequences, sequence_length, 1), dtype=int)
  print(ytra_ac.shape)


  ytra_ac_reshaped = ytra_ac.reshape((num_sequences, sequence_length, 1))

  ytra_ac_modified[:, :, 0] = ytra_ac_reshaped[:, :, 0]


  num_sequences_val = len(xval_ac) // sequence_length

  xval_ac_reshaped = xval_ac[:num_sequences_val * sequence_length].reshape((num_sequences_val, sequence_length, 38))

  i=0; j = 0; label = 0

  yval_ac_modified = np.zeros((num_sequences_val, sequence_length, 1), dtype=int)
  yval_ac_reshaped = yval_ac.reshape((num_sequences_val, sequence_length, 1))
  yval_ac_modified[:, :, 0] = yval_ac_reshaped[:, :, 0]

  early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

  model1.fit(xtra_ac_reshaped, ytra_ac_modified, epochs=200, batch_size=32, validation_data=(xval_ac_reshaped, yval_ac_modified), callbacks=[early_stopping])


  num_sequences_test = len(xtest_ac) // sequence_length

  xtest_ac_modified = xtest_ac[:num_sequences_test * sequence_length].reshape((num_sequences_test, sequence_length, 38))
  i=0; j = 0; label = 0

  pred_output1= model1.predict(xtest_ac_modified)
  # print(pred_output1)
  # Your input array
  array_of_arrays = pred_output1

  flattened_array = array_of_arrays.reshape(-1, array_of_arrays.shape[-1])

  result_array_ = [flattened_array[i] for i in range(len(flattened_array)) if i not in test_ind]
  result_array = np.array([array.tolist() for array in result_array_])
  # print(result_array, yt)
  # print(result_array.shape, yt.shape)
  yt = yt.T
  y_pred_a = np.where(result_array > 0.5, 1, 0)

  accuracy = calculate_accuracy(y_pred_a, yt)
  print("============......",accuracy)
  post_labels=make_partitions(wtest, result_array)
  post_l = np.array(post_labels)
  swapped_array = np.where(post_l == 0, 1.0, 0.0)

  accuracy_xtest_a = calculate_accuracy(post_l, yt)
  accuracy_xtest_a1 = calculate_accuracy(swapped_array, yt)
  print(accuracy_xtest_a,"original")
  # F1_score_WoPP_a = f1_score(ytest1, y_pred_a)
  # F1_score_WPP_a = f1_score(ytest1, post_labels)

  accuracy_all_folds_wopp_a.append(round(accuracy * 100, 3))
  accuracy_all_folds_wpp_a.append(round(accuracy_xtest_a * 100, 3))
  accuracy_all_folds_wpp_a1.append(round(accuracy_xtest_a1 * 100, 3))
  # f1score_all_folds_wopp_a.append(round(F1_score_WoPP_a * 100, 3))
  # f1score_all_folds_wpp_a.append(round(F1_score_WPP_a * 100, 3))

print(accuracy_all_folds_wopp_a)
'''average1 = statistics.mean(accuracy_all_folds_wopp_a)
std1 = statistics.stdev(accuracy_all_folds_wopp_a)
print("Average:", average1)
print("Standard Deviation:", std1)'''

print(accuracy_all_folds_wpp_a)
'''average2 = statistics.mean(accuracy_all_folds_wpp_a)
std2 = statistics.stdev(accuracy_all_folds_wpp_a)
print("Average:", average2)
print("Standard Deviation:", std2)'''