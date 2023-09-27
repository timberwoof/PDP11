# stopWatch.py
# python package for timing stuff
import sys
import time

class stopWatch():
    """One stopWatch object that tracks one method's duration. That's all."""
    def __init__(self, id):
        print(f'stopWatch({id}) init')
        self.id = id
        self.count = 0
        self.min = 100000000
        self.max = -1 # "uninitialized"
        self.sum = 0
        self.mean = -1 # "uninitialized"
        self.start = time.clock_gettime_ns
        print(f'stopWatch({id}) init done')

    def getId(self):
        return self.id

    def getMin(self):
        return self.min

    def getMean(self):
        return self.mean

    def getMax(self):
        return self.max

    def getSum(self):
        return self.sum

    def getCount(self):
        return self.count

    def restart(self):
        """Restarts the clock. You better call stop first if you want to accumulate that time!"""
        self.start = time.clock_gettime_ns

    def stop(self, timestop):
        """Stops the clock and calculates min, max, and mean."""
        duration = timestop - self.start
        self.min = min(duration, self.min)
        self.max = max(duration, self.max)
        self.sum = self.sum + duration;
        self.count = self.count + 1;
        self.mean = self.sum / self.count;

    def toString(self):
        """pad the id out so reports look nice"""
        pad = ""
        i = 0
        while i < len(self.id):
            pad = pad + " "
        reportmin = self.min
        if reportmin == sys.maxint:
            reportmin = -1
        return f'{self.id}{pad}\t{reportmin}\t{self.mean}\t{self.max}\t{self.sum}\t{self.count}'

    def identity(self):
        print(self.id)

class stopWatchList():
    """Manages a list of stopWatchAccumulator objects.
    Lets you obtain timing information for methods in your project."""
    def __init__(self):
        print('stopWatchList init')
        self.stopWatchList = {}

    def reset(self):
        """Reset stopWatch list, clear all stopWatches."""
        print('stopWatchList reset')
        self.stopWatchList = {}

    def start(self, id):
        """Initialize one stop watch for a method.
        Call this before the part whose duration you want to measure.
        After the section, call stop()."""
        print(f'stopWatchList start({id})')
        try:
            thisstopWatch = self.stopWatchList[id]
            print(f'stopWatchList start found {id}')
        except:
            thisstopWatch = stopWatch(id);
            self.stopWatchList[id] = thisstopWatch
            print(f'stopWatchList start created {id}')
        thisstopWatch.restart()

    def restart(self, id):
        """Reset and start an existing stopWatch.
        Call this if the stopWatch already exists and you want a new reading.
        After the section, call stop(id).
        id lets you have multiple stopWatches in one method"""
        print(f'stopWatchList restart({id})')
        self.remove(id)
        self.startPrivate(id)

    def stop(self, id):
        """Call this right after the part whose duration you want to measure.
        If the id cannot be found, returns error message.
        id lets you have multiple stopWatches in one method"""
        print(f'stopWatchList stop({id})')
        stoptime = time.clock_gettime_ns
        try:
            stopWatchAccumulator = self.stopWatchList[id]
            stopWatchAccumulator.stop(stoptime)
        except:
            print(f'WARN: stopWatchList stopPrivate could not find id {id}')

    def report(self):
        print("stopWatch Report")
        for thestopWatch in self.stopWatchList:
            print(thestopWatch.toString())
        print("stopWatch Report end")

    def getMean(self, id):
        """Returns the mean value of the accumulated stopWatch.<br>
	    If id cannot be found, returns -1.
	    id lets you have multiple stopWatches in one method"""
        try:
            thestopWatch = self.stopWatchList[id]
            return thestopWatch.getMean()
        except:
            return -1

    def toString(self, id):
        """Returns current state of this method's stopWatch.
        If the id cannot be found, returns error message.
        id lets you have multiple stopWatches in one method"""
        try:
            thestopWatch = self.stopWatchList[id]
            return thestopWatch.toString()
        except:
            return f'WARN: stopWatchList toString could not find id {id}'
