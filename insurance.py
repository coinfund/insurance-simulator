#!/usr/bin/env python

from scipy.stats import norm
from numpy import sqrt, ceil, maximum
from random import random

class Estimator():
  """
  Simple estimator for calculating premiums and/or payouts
  for a basic Bernoulli distribution based on:

    https://static1.squarespace.com/static/53442a39e4b06157f4464de8/t/582e8dcdcd0f688e8f4d53c3/1479445965306/Decentralized_Insurance_Scheme.pdf
  """

  def __init__(self, p, n=0, pi=.9999, P=None, P0=None):
    """
      Inputs:

        p:   probability of claim
        n:   number of obligors
        pi:  desired confidence level for solvency
        P:   payout (optional, fixed across all policies)
        P0:  premium (optional)

      Outputs:
      
        mu:      expected number of claims
        sigma:   std deviation of claims
        z:       z-score corresponding to pi-confidence
        k:       number of claims to collateralize
        P or P0: payout or premium is an output
        r:       the return multiple of the policies in this pool
        L:       total liability of the pool      
    """
    self.n    = n
    self.p    = p
    self.pi   = pi
    self.P    = P
    self.P0   = P0
    self.__calculate()
      
  def __calculate(self):
    """
    Calculates all of the parameters of the model, given
    p, n, and either P or P0, and optionally pi.
    """
    self.mu     = self.n * self.p
    self.sigma  = sqrt(self.n * self.p * (1.0 - self.p))
    self.z      = norm.ppf(self.pi)
    self.k      = ceil(self.mu + self.z * self.sigma)

    if self.P:
      self.P0   = self.k / self.n * self.P
    elif self.P0:
      self.P    = self.n / self.k * self.P0
    else:
      raise Exception('need either P or P0')

    self.r      = self.P / self.P0
    self.L      = self.n * self.P

  def __str__(self):
    return """
      n:     %s
      p:     %s
      pi:    %s
      mu:    %s
      sigma: %s
      z:     %s
      k:     %s
      P0:    %s
      P:     %s
      r:     %s
      L:     %s
    """ % (self.n, self.p, self.pi, self.mu, self.sigma, self.z, self.k, self.P0, self.P, self.r, self.L)

class InsurancePool():

  def __init__(self, p, P, seed=0):
    self.n = 0
    self.p = p
    self.P = P
    self.cap = seed
    self.claims  = 0
    self.issued  = 0
    self.inbound = 0

  def issue(self):

    self.n += 1
    self.issued += 1
    eff_n = self.cap / self.P
    pool = Estimator(self.p, n=eff_n, P=self.P)
    self.cap += pool.P0
    self.inbound += pool.P0
    print('selling policy at %0.2f, k = %s, effective capitalization supports k = %d' % (pool.P0, pool.k, self.cap / self.P))
    self.L = self.n * self.P

  def claim(self):
    self.n -= 1
    self.cap -= self.P
    self.claims += 1
    if self.cap < 0:
      raise Exception('pool is insolvent')

  def expire(self):
    self.n -= 1

  def __str__(self):
    return """
      n:       %s
      P:       %s
      cap:     %s
      L:       %s

      issued:  %-4d   (pool = %0.2f / L = %0.2f -> %0.2f pct)
      claims:  %-4d   (%0.2f)
    """ % (self.n, self.P, self.cap, self.L, self.issued, self.inbound, self.issued*self.P, (self.inbound / (self.issued*self.P) * 100), self.claims, self.claims*self.P)

def start(p = 0.05, P=500):
  """
  Pool simulation.
  """

  pool = InsurancePool(p, P, seed=20000)
  
  # Issue 1000 policies
  for i in range(1000):
    pool.issue()
  
  # Randomly issue more policies or expire/claim
  # existing ones...
  for i in range(10000):
    rnd = random()
    if rnd < 0.5:
      pool.issue()
    else:
      rnd = random()
      if rnd < p:
        print('policy is claimed')
        pool.claim()
      else:
        print('policy is expired')
        pool.expire()
      print(pool)

  # Redeem or expire policies until pool
  # is empty...
  while pool.n > 0:
    rnd = random()
    if rnd < p:
      print('policy is claimed')
      pool.claim()
    else:
      print('policy is expired')
      pool.expire()
    print(pool)

  print("""
    excess capital: %0.2f
    payouts:        %d
    payouts value:  %0.2f
  """ % (pool.cap, pool.claims, pool.claims * pool.P))

if __name__ == '__main__':
  start()
