# Data on the cost and "age" of each of the N = 10 car models are given cars. 
# Write a program that determines the average cost of cars whose "age" exceeds X years.

import datetime

n = 10
age = int(input('set the age value = '))
carYear = [2000,2008,2017,1999,1987,2020,2013,2010,2011,2004,]
carPrice = [2000,4000,3500,4700,18000,22000,120,8000,6500,4800,]


def averagePrice(n, age):
    sysYear = datetime.datetime.now().year - age
    average = 0
    i = 0
    j = 0
    
    while i < n:
        if carYear[i] <= sysYear:
            average += carPrice[i]
            j+=1
        i+=1
    average /= j
    return average

print('AveragePrice is: %d' % averagePrice(n, age))
