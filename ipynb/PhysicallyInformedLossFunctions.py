import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

class ThresholdedMSELoss(nn.Module):
    """
    This class contains a loss function that use a mean-squared-error loss for reasonable predictions
    and an exponential penalty for unreasonable predictions. They inherit from torch.nn.Module. For 
    physically unreasonable conditions, prediction loss is more severely calculated. What qualifies as
    reasonable is based on empirically gathered datasets and literature reported boundaries of performance.
    
    For the following predictions that are improbable, the loss is penalized:
    - X < lower
    - X > upper
    """

    def __init__(self, lower, upper):
        super(ThresholdedMSELoss, self).__init__()
        self.lower = lower
        self.upper = upper

    def forward(self, predictions, labels):
        
        result_list = torch.zeros(predictions.size(0))
        element_count = 0
        
        for x, y in zip(predictions, labels):
            
            # if (x >= 0) == 1 (True)
            if torch.le(x, torch.tensor([self.lower])) == torch.tensor([1]):
                #Exponential MSE for x <= 0
                # Need to use only torch.nn.Function() and torch.() functions for autograd to track operations
                error = torch.add(x, torch.neg(y)) #error = x + (-y)
                element_result = torch.pow(error, 2)
                element_result = torch.pow(element_result, 1)
            

           # if (x <= 6) == 1 (True)
            elif torch.ge(x, torch.tensor([self.upper])) == torch.tensor([1]):
                #exponential MSE for x >= 6
                error = torch.add(x, torch.neg(y))
                element_result = torch.pow(error, 2)
                element_result = torch.pow(element_result, 1)

            # all other values of x
            else:
                error = torch.add(x, torch.neg(y))
                element_result = torch.pow(error, 2)
                
            result_list[element_count] = element_result
            element_count+=1
            
            
            # Average of all the squared errors
            result = result_list.mean()

            return result


class Accuracy(nn.Module):
    """
    Simple class to interate through predictions and labels to determine overall accuracy of a model
    """
    
    def __init__(self, acc_thresh = 0.1):
        super(Accuracy, self).__init__()
        self.acc_thresh = acc_thresh
        
    def forward(self, predictions, labels):
        element_count = 0
        correct = 0
        
        accuracy_list = []
        
        for x, y in zip(predictions, labels):
            
            error = torch.tensor(y-x)
            
            #if precision <= accuracy threshold, count as correct
            if torch.le(torch.div(error, y), torch.tensor(self.acc_thresh)) == torch.tensor([1]):
                correct += 1
                element_count += 1

            else:
                element_count += 1
            
            accuracy = (correct/element_count) * 100
            accuracy_list.append(accuracy)
            
        acc_list = torch.tensor(accuracy_list)
            
        avg_acc = acc_list.mean()

        return avg_acc
    
class MAPE(nn.Module):
    """
    Simple class to interate through pytorch tensors of predictions and ground-tuths to calculate 
    the Mean Absolute Percent Error (MAPE).
    """
    
    def __init__(self):
        super (MAPE, self).__init__()
        
    def forward(self, predictions, labels):
        
        absolute_percent_error_list = []
        count = 0
        
        for x, y in zip(predictions, labels):
            count += 1
            
            error = y - x
            
            ae = np.absolute(error)
            
            ape = ae/y
            
            absolute_percent_error_list.append(ape)
            
        mape = np.sum(absolute_percent_error_list) / count
        mape = mape * 100
        
        return mape
    
    