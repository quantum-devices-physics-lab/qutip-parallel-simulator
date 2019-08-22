from QutipSimulator import *
import numpy as np
from qutip import *

# This is script is an example of how to use QutipSimulator

# Create a class that inherit class QuantumSystem
# One have to implement the method run, which is the one that will be runned in parallel
class MyQuantumExperiment(QuantumSystem):
    
    def run(self):

        #prep is an dictionary passed in the prepare method
        #define different variables to be used on simulation
        oscillator_i = self.prep["oscillator"]
        t = self.prep["time"]

        H = self.get_Hamiltonian()

        # when using c_ops, always calls this beforehand.
        self.update_dissipative_operations()

        #Here we are calculating the power spectrum of a given system
        corr = correlation_2op_1t(H, self.psi0, t, self.c_ops, self.oscillators[oscillator_i].a.dag(), self.oscillators[oscillator_i].a)
        w, s = spectrum_correlation_fft(t, corr)

        return (corr,w,s)

# this returns the list of tasks to be computed on parallel
# We define the objects of MyQuantumExperiment and add it to a list
def getTasks():
    t = np.linspace(0,100,5000)
    
    Tasks = []

    N=5
    Ta = 0
    kappa = 0.25
    
    # We add three uncoupled oscillators
    # N is the number of focks states
    # 4.5, 5.0 amd 5.5 is the frequency
    # kappa is the dissipation constants
    # Ta is the temperatura
    QS1 = MyQuantumExperiment()
    QS1.add_oscillator(N,4.5,kappa,Ta)
    QS1.add_oscillator(N,5.0,kappa,Ta)
    QS1.add_oscillator(N,5.5,kappa,Ta)
    # define the initial state
    QS1.set_initial_state(tensor(basis(N,0),basis(N,0),basis(N,0)))
    

    QS2 = MyQuantumExperiment()
    QS2.add_oscillator(N,4.5,kappa,Ta)
    QS2.add_oscillator(N,5.0,kappa,Ta)
    QS2.add_oscillator(N,5.5,kappa,Ta)
    QS2.set_initial_state(tensor(basis(N,0),basis(N,0),basis(N,0)))

    #The System 2 is exactly like the first one but now the harmonic oscillators are coupled
     couplings = [0.1,0.15]
    for idx,g in enumerate(couplings):
        QS2.add_coupling(g*QS2.oscillators[idx].a.dag()*QS2.oscillators[idx].a*
                         (QS2.oscillators[2].a.dag()+QS2.oscillators[2].a.dag()))


    # We prepare the system measurement
    QS1.prepare(oscillator=0,time=t)
    QS2.prepare(oscillator=0,time=t)
    
    Tasks.append(QS1)
    Tasks.append(QS2)
    
    return Tasks

if __name__ == "__main__":
    tasks = getTasks()

    # this is the main method
    # the first method is the name of the simulations
    # the second is the list of tasks
    # the third is the system args passed to the script
    simulate("Qutip Simulation",tasks,sys.argv)
