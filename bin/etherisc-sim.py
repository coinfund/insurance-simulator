#!/usr/bin/env python

# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-11-21 21:27:48
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-11-21 21:33:02

from etherisc.insurance import InsurancePool
from numpy.random import poisson
from random import random

def start(p = 0.05, P=100, lam=10):
  """
  Pool simulation.
  """

  pool = InsurancePool(p, P, seed=1000)
  
  for i in range(1000):
    # assume policies come in with a Poisson
    # distribution at a certain rate per day
    if i % 2 == 0:
      policies = poisson(lam=lam)
      for _ in range(policies):
        pool.issue()

    else:    
      arrivals = policies
      for _ in range(arrivals):
        rnd = random()
        if pool.n > 0:
          if rnd < p:
            pool.claim()
          else:
            pool.expire()
        else:
          break


    # pool.p = pool.claims / pool.issued

    print(pool)
    input('---> press any key to continue\n')

if __name__ == '__main__':
  start()