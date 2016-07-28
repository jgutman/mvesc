import time

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()
        return self
    
    def time_check(self):
        return time.time() - self.tstart

    def __exit__(self, type, value, traceback):
        if self.name:
            print("{}:".format(self.name), end = ' ')
        print('{:.2} seconds elapsed'.format(time.time() - self.tstart))
        
def main():
    with Timer('test') as t:
        print(t.name)
        for i in range(10000):
            x = i*3
        print("doing some stuff took {:.2} seconds".format(t.time_check()))
        for i in range(10000):
            x = i*4
        print("did some other stuff")

if __name__ == "__main__":
    main()
