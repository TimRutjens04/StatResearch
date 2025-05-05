from threading import Lock, Semaphore

class ReusableBarrier:
    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Lock()
        self.turnstile1 = Semaphore(0)
        self.turnstile2 = Semaphore(1)
    
    def phase1(self):
        with self.mutex:
            self.count += 1
            if self.count == self.n:
                self.turnstile2.acquire()
                self.turnstile1.release()
        self.turnstile1.acquire()
        self.turnstile1.release()

    def phase2(self):
        with self.mutex:
            self.count -= 1
            if self.count == 0:
                self.turnstile1.acquire()
                self.turnstile2.release()
        self.turnstile2.acquire()
        self.turnstile2.release()

    def wait(self):
        self.phase1()
        self.phase2()