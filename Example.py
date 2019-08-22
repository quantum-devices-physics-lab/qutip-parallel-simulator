from QutipSimulator import *
import numpy as np
from qutip import *

class MyQuantumExperiment(QuantumSystem):
    
    def run(self):
        oscillator_i = self.prep["oscillator"]
        t = self.prep["time"]
        H = self.get_Hamiltonian()
        self.update_dissipative_operations()
        #result = mesolve(H, self.psi0, t, self.c_ops,self.operators)
        
        corr = correlation_2op_1t(H, self.psi0, t, self.c_ops, self.oscillators[oscillator_i].a.dag(), self.oscillators[oscillator_i].a)
        
        w, s = spectrum_correlation_fft(t, corr)
        
        return (corr,w,s)

def getTasks():
    t = np.linspace(0,100,5000)
    
    Tasks = []
    
    
    QS1 = MyQuantumExperiment()
    N=5
    Ta = 0
    kappa = 0.25
    QS1.add_oscillator(N,4.5,kappa,Ta)
    QS1.add_oscillator(N,5.0,kappa,Ta)
    QS1.add_oscillator(N,5.5,kappa,Ta)
    QS1.set_initial_state(tensor(basis(N,0),basis(N,0),basis(N,0)))
    

    QS2 = MyQuantumExperiment()

    QS2.add_oscillator(N,4.5,kappa,Ta)
    QS2.add_oscillator(N,5.0,kappa,Ta)
    QS2.add_oscillator(N,5.5,kappa,Ta)
    QS2.set_initial_state(tensor(basis(N,0),basis(N,0),basis(N,0)))

    couplings = [0.1,0.15]

    for idx,g in enumerate(couplings):
        QS2.add_coupling(g*QS2.oscillators[idx].a.dag()*QS2.oscillators[idx].a*
                         (QS2.oscillators[2].a.dag()+QS2.oscillators[2].a.dag()))
        
    
    
    QS3 = MyQuantumExperiment()

    QS3.add_oscillator(N,4.5,kappa,Ta)
    QS3.add_oscillator(N,5.0,kappa,Ta)
    QS3.add_oscillator(N,5.5,kappa,Ta)
    QS3.set_initial_state(tensor(basis(N,0),basis(N,1),basis(N,0)))

    couplings = [0.1,0.15]
    
    QS4 = MyQuantumExperiment()

    QS4.add_oscillator(N,4.5,kappa,Ta)
    QS4.set_initial_state(basis(N,0))

    
    QS1.prepare(oscillator=0,time=t)
    QS2.prepare(oscillator=0,time=t)
    QS3.prepare(oscillator=0,time=t)
    QS4.prepare(oscillator=0,time=t)
    
    Tasks.append(QS1)
    Tasks.append(QS2)
    Tasks.append(QS3)
    Tasks.append(QS4)
    
    return Tasks

if __name__ == "__main__":
    tasks = getTasks()
    simulate("Qutip Simulation",tasks,sys.argv)
