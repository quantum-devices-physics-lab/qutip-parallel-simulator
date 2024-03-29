import matplotlib.pyplot as plt
import numpy as np
from qutip import *
import multiprocessing as mp
import scipy.constants as sc
import sys
import logging
import datetime
import yagmail
import getpass
import time


class QuantumOscillator():
    def __init__(self,i,n,w,kappa,n_th):
        self.i = i
        self.n = n
        self.w = w
        self.kappa = kappa
        self.n_th = n_th
        
        self.a = destroy(self.n)

class Executable(object):
    def prepare(self,**prep):
        self.prep = prep
        
    def run(self,**kwargs):
        pass

class Task(object):
    
    def __init__(self, listtask):
        self.ltask = listtask
        
    def add(self, task):
        self.ltask.append(task)
    
    def execute(self,pool):
        pass
    
    def count(self):
        return len(self.ltask)
    
class QuantumSystem(Executable):
    def __init__(self):
        super().__init__()
        self.oscillators = []
        self.couplings = []
        self.c_ops = []
        self.operators = []
    
    def add_oscillator(self,n,w,kappa,Ta,n_th=0):
        
        
        i_osc = len(self.oscillators)
        if n_th == 0 and Ta > 0.0:
            n_th = 1/(np.exp(sc.hbar*w*1e9/(sc.k*Ta))-1)
       
        
        o = QuantumOscillator(i_osc,n,w,kappa,n_th)
        
        for osc in self.oscillators:
            osc.a = tensor(osc.a,qeye(o.n))
            o.a = tensor(qeye(osc.n),o.a)

        self.oscillators.append(o)
   
    def add_coupling(self,c):
        self.couplings.append(c)
        
    def set_initial_state(self,psi0):
        self.psi0 = psi0
    
    def update_dissipative_operations(self):
        self.c_ops = []
        for osc in self.oscillators:
            # cavity relaxation
            rate = osc.kappa * (1 + osc.n_th)
            if rate > 0.0:
                self.c_ops.append(np.sqrt(rate) * osc.a)

                # cavity excitation, if temperature > 0
            rate = osc.kappa * osc.n_th
            if rate > 0.0:
                self.c_ops.append(np.sqrt(rate) * osc.a.dag())
                
    def get_Hamiltonian(self):
        H = 0
        
        for osc in self.oscillators:
            H += osc.w*osc.a.dag()*osc.a
        
        for coupling in self.couplings:
            H += coupling
       
        return H
   

    
    
def log_email(text,title):
    if "yag" in globals() and "tomail" in globals():
        yag.send(to=tomail,subject=title,contents=text)

def simulate(name,task,argv):

    filename = name.replace(" ","_")
    
    if len(sys.argv)>=3:
        for idx,arg in enumerate(sys.argv):
            if(arg == "-from"):
                global yag
                frommail= sys.argv[idx+1]
                password = getpass.getpass()
                yag = yagmail.SMTP(frommail, password)
            if(arg == "-to"):
                global tomail
                tomail = sys.argv[idx+1]

    logging.basicConfig(level=logging.DEBUG)    
    logger = logging.getLogger(name)

    handler = logging.FileHandler('log_{}_{}.log'.format(filename,datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    
    task_count = task.count()
    
    cpu_count = mp.cpu_count()
    
        
    logger.info("Starting Simulation")
    log_email("Starting Simulation",name)

    logger.info("#CPU {}".format(cpu_count))
    log_email("#CPU {}".format(cpu_count),name)
    

    try:
        t_start = time.time()
        time_1 = []

        pool = mp.Pool(processes = cpu_count)

        results = task.execute(pool)

        passedAnHour = 0
        while True:
            incomplete_count = sum(1 for x in results if not x.ready())

            if incomplete_count == 0:
                log_email("[100.0%] of the simulation calculated",name)
                logger.info("[100.0%] of the simulation calculated")
                log_email("All done! Total time: %s"%datetime.timedelta(seconds=int(dif_time)),name)
                logger.info("All done! Total time: %s"%datetime.timedelta(seconds=int(dif_time)))
                break
            else:
                p = float(task_count - incomplete_count) / task_count * 100
                dif_time = (time.time()-t_start)
          

            if(int(dif_time/3600)-passedAnHour > 0):
                passedAnHour = int(dif_time/3600)
                log_email("[%4.1f%%] of the simulations calculated, progress time: %s "%(p,datetime.timedelta(seconds=int(dif_time))),name)
            logger.info("[%4.1f%%] of the simulations calculated, progress time: %s "%(p,datetime.timedelta(seconds=int(dif_time))) )
            
            
            time.sleep(1)

        while not all([ar.ready() for ar in results]):
            for ar in results:
                ar.wait(timeout=0.1)


        pool.close()
        pool.join
        
        

    


        log_email("Saving acquired data",name)
        logger.info("Saving acquired data")

        data = np.array([ar.get() for ar in results])

        np.save("data_{}_{}".format(filename,datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")),data);
    except Exception as e:
        log_email("Simulation interrupted by error",name)
        logger.exception(e)
        pool.terminate()
        pool.join()
        raise e
    
    log_email("End of simulation",name)
    logger.info("End of simulation")

    handler.close()
    logger.removeHandler(handler)
    logging.shutdown()
    
def simulateSerially(name,tasks,argv):

    filename = name.replace(" ","_")
    
    if len(sys.argv)>=3:
        for idx,arg in enumerate(sys.argv):
            if(arg == "-from"):
                global yag
                frommail= sys.argv[idx+1]
                password = getpass.getpass()
                yag = yagmail.SMTP(frommail, password)
            if(arg == "-to"):
                global tomail
                tomail = sys.argv[idx+1]

    logging.basicConfig(level=logging.DEBUG)    
    logger = logging.getLogger(name)

    handler = logging.FileHandler('log_{}_{}.log'.format(filename,datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    
    logger.info("Starting Simulation")
    log_email("Starting Simulation",name)
    

    try:
        
        for task in tasks:
            qsystem = task[0]
            data = qsystem.run()

            log_email("Saving acquired data","{} - {}".format(name,task[1]))
            logger.info("Saving acquired data {}".format(task[1]))

            np.save("data_{}_{}_{}".format(filename,datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),task[1]),data);
            
    except Exception as e:
        log_email("Simulation interrupted by error",name)
        logger.exception(e)

        raise e
    
    log_email("End of simulation",name)
    logger.info("End of simulation")

    handler.close()
    logger.removeHandler(handler)
    logging.shutdown()    





