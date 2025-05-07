from threading import Lock, Semaphore, Condition
from enum import Enum
from dataclasses import dataclass
from typing import Dict
import time
import random
from reusable_barrier import ReusableBarrier

'''
Machine and gym setup logic
'''
class MachineTypes(Enum):
    BENCH_PRESS = "bench press"
    TREADMILL = "treadmill"
    LEG_PRESS = "leg press"
    LAT_PULLDOWN = "lat pulldown"
    CHEST_PRESS = "chest press"
    CALF_RAISE = "calf raise"

@dataclass
class Machine:
    id: int
    type: MachineTypes
    in_use: bool = False
    current_user: int = None

class GymConfig:
    def __init__(self):
        self.machine_counts = {
            MachineTypes.BENCH_PRESS: 3,
            MachineTypes.TREADMILL: 10,
            MachineTypes.LEG_PRESS: 4,
            MachineTypes.LAT_PULLDOWN: 4,
            MachineTypes.CHEST_PRESS: 2,
            MachineTypes.CALF_RAISE: 1
        }

# Monitor super class:
class SuperMonitor(object):
    def __init__(self, lock = Lock()):
        self._lock = lock

    def Condition(self):
        return Condition(self._lock)
    
    init_lock = __init__

# Actual monitor:
class Monitor(SuperMonitor):
    def __init__(self, config: GymConfig):
        self.init_lock()

        #Capacity control (fencing)
        self.capacity = Semaphore(20)

        self.needs_spotter = self.Condition()
        self.spotter_available = False

        self.warmed_up = self.Condition()
        self.warmed_up_users = set()

        self.box_class_barrier = ReusableBarrier(3) #Requires 3 participants
        self.box_class_ready = self.Condition()
        self.box_class_ongoing = False

        self.machine_locks = {
            MachineTypes.BENCH_PRESS: Semaphore(config.machine_counts[MachineTypes.BENCH_PRESS]),
            MachineTypes.TREADMILL: Semaphore(config.machine_counts[MachineTypes.TREADMILL]),
            MachineTypes.LEG_PRESS: Semaphore(config.machine_counts[MachineTypes.LEG_PRESS]),
            MachineTypes.LAT_PULLDOWN: Semaphore(config.machine_counts[MachineTypes.LAT_PULLDOWN]),
            MachineTypes.CHEST_PRESS: Semaphore(config.machine_counts[MachineTypes.CHEST_PRESS]),
            MachineTypes.CALF_RAISE: Lock()
        }

        #Initialize machines with unique IDs
        self.machines: Dict[int, Machine] = {}
        current_id = 0

        for machine_type, count in config.machine_counts.items():
            for _ in range(count):
                self.machines[current_id] = Machine(
                    id = current_id,
                    type = machine_type
                )
                current_id += 1

    # def __enter__(self):
    #     self._lock.acquire()
    #     return self

    # def __exit__(self):
    #     self._lock.release()
    #     return self
    
    def complete_warmup(self, user_id: int):
        with self._lock:
            print(f"User {user_id} completed warm-up")
            self.warmed_up_users.add(user_id)
            self.warmed_up.notify_all()

    def request_machine(self, user_id: int, machine_type: MachineTypes, has_warmed_up: bool = False):
        if machine_type == MachineTypes.TREADMILL:
            has_warmed_up = True

        if not has_warmed_up and user_id not in self.warmed_up_users:
            with self._lock:
                print(f"User {user_id} is warming up")
                self.warmed_up.wait()

        self.machine_locks[machine_type].acquire()

        if machine_type == MachineTypes.BENCH_PRESS:
            with self._lock:
                while not self.spotter_available:  
                    print(f"User {user_id} waiting for spotter")
                    self.needs_spotter.wait()
                self.spotter_available = False

        with self._lock:
            for machine in self.machines.values():
                if machine.type == machine_type and not machine.in_use:
                    machine.in_use = True
                    machine.current_user = user_id
                    print(f"{machine.type.value} {machine.id} in use by user {user_id}")
                    return machine.id
    
    def release_machine(self, machine_id: int):
        with self._lock:
            machine = self.machines[machine_id]
            machine.in_use = False
            machine.current_user = None
            self.machine_locks[machine.type].release()

            if machine.type == MachineTypes.BENCH_PRESS:
                self.spotter_available = True
                self.needs_spotter.notify()

    def join_box_class(self, user_id: int):
        print(f"User {user_id} waiting for box class to start")
        self.box_class_barrier.phase1()

        with self._lock:
            if not self.box_class_ongoing:
                print("Box class starting")
                self.box_class_ongoing = True
        
        #Simulate some time for box class
        time.sleep(2)

        self.box_class_barrier.phase2()

        with self._lock:
            if self.box_class_ongoing:
                print("Box class finished")
                self.box_class_ongoing = False


