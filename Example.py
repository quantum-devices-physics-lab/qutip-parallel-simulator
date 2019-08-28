from QutipSimulator import *
import numpy as np
from qutip import *

# This is script is an example of how to use QutipSimulator

# Create a class that inherit class QuantumSystem
# One have to implement the method run, which is the one that will be runned in parallel
class MyQuantumExperiment(QuantumSystem):
    
    def run(self,**kwargs):
        oscillator_i = kwargs["oscillator"]
        t = self.prep["time"]
        H = self.get_Hamiltonian()
        self.update_dissipative_operations()
        #result = mesolve(H, self.psi0, t, self.c_ops,self.operators)
        
        corr = correlation_2op_1t(H, self.psi0, t, self.c_ops, self.oscillators[oscillator_i].a.dag(), self.oscillators[oscillator_i].a)
        
        w, s = spectrum_correlation_fft(t, corr)
        
        return (corr,w,s)

        
class MyTask(Task):
    def execute(self,pool):
        return [pool.apply_async(a1[0].run,kwds=a1[1]) for a1 in self.ltask]


def setOscillators(QS,N,kappa,Ta,freqs):
    for w in freqs:
        QS.add_oscillator(N,w,kappa,Ta)


def getTasks2():
    
    Tasks = []
    
    t = np.linspace(0,50,100)

    N=5
    Ta = 30e-3
    kappa = 0.0005

    freqs = [4.5*2*np.pi,5.0*2*np.pi,5.5*2*np.pi]
    couplings = np.array([0.1,0.15])*2*np.pi

    QS1 = MyQuantumExperiment()
    setOscillators(QS1,N,kappa,Ta,freqs)
    QS1.set_initial_state(tensor(basis(N,1),basis(N,0),basis(N,0)))

    QS1.prepare(time=t)

    
    Tasks.append((QS1,{"oscillator":0}))
    
    return Tasks

if __name__ == "__main__":
    
    task = MyTask(getTasks2())

    simulate("Qutip frequency shift Simulation",task,sys.argv)
