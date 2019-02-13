#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 15:54:55 2019

@author: evrardgarcelon
"""


import utils
import numpy as np
from cross_validation import CrossValidation
from kernel_knn import KernelKNN
from kernel_lr import KernelLogisticRegression
from svm import SVM

class RandomHyperParameterTuningPerKernel(object) :
    
    def __init__(self,clf,kernel, parameter_grid, X, y, n_sampling) :
        self.clf = clf
        self.kernel = kernel
        self.parameter_grid = parameter_grid
        self.X = X
        self.y = y
        self.n = n_sampling
        self.kernel_parameters = utils.get_kernel_parameters(self.kernel)
        self.kernels = parameter_grid['kernel']
        if isinstance(clf(kernel = kernel),KernelKNN) :
            self.clf_parameters =  ['n_neighbors']
        elif isinstance(clf(kernel = kernel),SVM) :
            self.clf_parameters = ['C']
        elif isinstance(clf(kernel = kernel),KernelLogisticRegression) :
            self.clf_parameters =  ['la','n_iter']
        else :
            raise Exception('Wrong classifier')
    
    def fit(self) :
        self.parameters = {}
        self.scores = {}
        for j in range(self.n) :
            temp_parameters = {}
            for parameter_name in self.kernel_parameters :
                temp_parameters[parameter_name] = self.parameter_grid[parameter_name].rvs()
            for parameter_name in self.clf_parameters : 
                temp_parameters[parameter_name] = self.parameter_grid[parameter_name].rvs()
            self.parameters[j] = temp_parameters
            temp_clf = self.clf(**temp_parameters)
            temp_clf.fit(self.X,self.y)
            CV = CrossValidation(self.X, self.y, temp_clf)
            mean_acc, std_acc = CV.mean_acc(), CV.std_acc()
            mean_recall, std_recall = CV.mean_recall_score(), CV.std_recall_score()
            mean_precision, std_precision = CV.mean_precision_score(), CV.std_precision_score()
            mean_f1_score, std_f1_score = CV.mean_f1_score(), CV.std_f1_score()
            temp_report = {'mean acc' : mean_acc,
                    'std acc' : std_acc,
                    'mean recall' : mean_recall,
                    'std recall' : std_recall,
                    'mean precision' : mean_precision,
                    'std precision' : std_precision,
                    'mean f1 score' : mean_f1_score,
                    'std f1 score' : std_f1_score}
            self.scores[j] = temp_report
            
            
class RandomHyperParameterTuning(object):
    
    def __init__(self, classifier, parameter_grid, X, y, n_sampling, criteria = 'accuracy') : 
        
        self.clf = classifier
        self.parameter_grid = parameter_grid
        self.clf = classifier
        self.X = X
        self.y = y
        self.n = n_sampling
        self.criteria = criteria
    
    def fit(self) :
        
        self.accuracy = {}
        self.parameters = {}
        for kernel in self.kernels :
            temp = RandomHyperParameterTuningPerKernel(self.clf,kernel, self.parameter_grid, self.X, self.y, self.n)
            scores = temp.scores()[self.criteria]
            self.parameters[kernel] = temp.parameters[np.argmax(np.array(scores))]
            self.accuracy[kernel] = scores
    
    def best_parameters(self) :
        
        max_acc,argmax = 0,0
        for kernel in self.kernels :
            acc = np.max(np.array(self.accuracy[kernel]))
            if acc > max_acc :
                max_acc = acc
                argmax = np.argmax(np.array(self.accuracy[kernel]))
        best_kernel = self.kernels[argmax]
        best_parameters = self.parameters[best_kernel]
        return np.array([best_kernel] + list(best_parameters))
            
            
            
            
            
        
        
        