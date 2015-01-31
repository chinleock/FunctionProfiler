"""
FcnProfiler.py
It's a module developed to timing and memory profiling for a function.

Leo Chin, 2015.1.30

"""
################################### Imports ###################################
import os as OS
import cProfile as PROFILE
import platform as PLATFORM
import pstats as PSTATS
import sys as SYS
from memory_profiler import profile as MP
from psutil import virtual_memory as VM
from test import pystone as PYSTONE

#### Loading Packages Based on Python Version ####
if SYS.version[0] == '3':
    from io import StringIO
else:
    from cStringIO import StringIO

############################## Global Utilities ###############################
def iteritems(d):
    try:
        return d.iteritems()
    except AttributeError:
        return d.items()

######################### Class for Capture the Output ########################
class OutputCatcher(list):
    """
    This class is designed for catching the printouts for a function.
    USAGE:
        with OutputCatcher as printouts:
            your_function()
        printouts.pop() for retrieving each printout from the last
    """
    def __enter__(self):
        self._stdout = SYS.stdout
        SYS.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        SYS.stdout = self._stdout

######################### Class for Profile the Function ######################
class FunctionProfiler(object):
    """
    This class is designed for profiling the time and memory for a function.
    USAGE:
        #### Target Function ####
        def testFunction(param1, param2):
            return param1 + param2
            
        myProfiler = FunctionProfiler()
        calls, time = myProfiler.profileTime('testFunction', 1,2)
        memoryUsage = myProfiler.profileMemory('testFunction', 1,2)
        
    ATTRIBUTES:
        envInfo (str): Test machine info: Python version, OS, Physical Memory..
        iteration (int): Number of iterations for profiling
        pystone (float): PyStone based on Python IDE
        benchmarkTime (float): Converted Benchmark Time from PyStone
         
    METHODS:
        resetIterations(iteration): Reset the iteration for profiling,
                                    Default is 50
        profileTime(fcnName, *fcnParam): Profile time of the function.
            Output is (number of CPU calls (int), CPU time (float))
        profileMemory(fcnName, *fcnParam): Profile memory of the function.
            Output is the memory_usage (float)
        runctx(cmd, globals, locals): Execute External Function or command line
        
    """
    def __init__(self, iteration = 50):
        #### Set Input Parameters to Class Attributes #### 
        for key, value in iteritems(locals()):
            if key != 'self':
                setattr(self, key, value)
        
        #### Record System Information ####
        physicalMem = float("{0:.2f}".format(VM().total / (1024)**3))
        self.envInfo = "Python " + PLATFORM.python_version()
        self.envInfo += " on " + PLATFORM.system() + "-"
        self.envInfo += PLATFORM.release() 
        self.envInfo += " with " + str(physicalMem) + "GB Memory, "
        self.envInfo += PLATFORM.machine() + (" machine")
        
        #### Record PyStone and Benchmark Time ####
        accumTime = 0.
        accumPystone = 0.
        for i in range(50):
            BENCHMARK_TIME, PYSTONES = PYSTONE.pystones()
            accumTime += BENCHMARK_TIME
            accumPystone += PYSTONES
        avgBechmarkTime = accumTime / 50.
        avgPystone = accumPystone / 50.
        self.pystone = avgPystone
        self.benchmarkTime = avgBechmarkTime
    
    #### Reset the Iterations ####    
    def resetInterations(self, iteration):
        self.iteration = iteration
    
    #### Profile Time ####        
    def profileTime(self, fcnName, *fcnParam):   
        totalTime = 0.
        totalCall = 0
        inFcn = fcnName + str(fcnParam)
        for i in range(self.iteration):
            PROFILE.run(inFcn, fcnName)
            stats = PSTATS.Stats(fcnName)
            totalTime += stats.total_tt
            totalCall += stats.total_calls
        calls = int(stats.total_calls / self.iteration)
        time = float("{0:.6f}".format(stats.total_tt / self.iteration))
        return calls,time 

    @MP(precision = 6)
    def runctx(self, cmd, globals, locals):
        try:
            exec(cmd, globals, locals)
        finally:
            print("Input Function " + str(cmd) + " is not executed")
            pass
    
    #### Profile Memory ####
    def profileMemory(self, fcnName, *fcnParam):
        import __main__
        inFcn = fcnName + str(fcnParam)
        dict = __main__.__dict__
        with OutputCatcher() as memPrintOuts:
            self.runctx(inFcn, dict, dict)
        while len(memPrintOuts) > 0:
            eachPrint = memPrintOuts.pop()
            if "exec(cmd, globals, locals)" in eachPrint:
                memString = eachPrint.split("   ")[2].split()[0]
                break
        if 'memString' not in locals():
            print("Failed to profile memory")
            memString = "-1"
        return float(memString)
        