#!/usr/bin/env pythonw2.7
import numpy as np
from scipy.optimize import fmin_slsqp
import json
import cloud

def qp(Q, mu):
    Q = np.matrix(Q)
    mu = np.array(mu)
    tao = 0.5
    x0 =  np.random.rand(len(mu),1) 
    constrain1 = lambda x : np.sum(x) - 1
    constrain2 = lambda x : np.all(x>=0) and 5 or -5
    bound = [(0, 1)] * len(x0)
    fun = lambda x : np.dot( np.dot(x.T, Q), x) - tao * np.dot(mu.T, x)
    xopt = fmin_slsqp(fun, x0, eqcons=[constrain1],  bounds=bound)
    return xopt.tolist()
    
if __name__ == '__main__':
    mu = [1,2,3]
    Q = [[1,0,0], [0,1,0], [0,0,1]]
    print "mu", mu
    print 'Q', Q
    res = qp(Q, mu)
    print json.dumps( res )
    print cloud.rest.publish(qp, "scipy_qp")
    #print cloud.result(18)