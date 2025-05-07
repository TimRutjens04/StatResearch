from gym import *
import queue
from threading import Thread

# Example usage
monitor = Monitor(GymConfig())
user_queue = queue.Queue()
active_users = set()
user_counter = 0
running = True

def user_manager():
    global user_counter
    while running:
        machine_types = list(MachineTypes)
        random_workout = random.sample(machine_types, k=random.randint(2, 5))

        join_box = random.random() < 0.1       
        user_queue.put((user_counter, random_workout, join_box))
        user_counter += 1

        time.sleep(2)

def process_users():
    while running:
        try:
            user_id, workout, join_box = user_queue.get(timeout=1)
            if join_box:
                print(f"User {user_id} will join box class")
                t = Thread(target=user_thread, args=(user_id, [], join_box))
            else:
                t = Thread(target=user_thread, args=(user_id, workout, join_box))
            t.start()
        except queue.Empty:
            continue


def user_thread(user_id, routines, join_box = False):
    """Simulate a user working out with their preferred machines"""
    print(f"User {user_id} waiting to enter")
    monitor.capacity.acquire()
    try:
        monitor.complete_warmup(user_id)

        if join_box:
            monitor.join_box_class(user_id)
        
        for machine_type in routines:
            machine_id = monitor.request_machine(user_id, machine_type)
            print(f"User {user_id} exercising on {machine_type.value}")
            # Simulate exercise time
            time.sleep(random.uniform(1, 3))
            monitor.release_machine(machine_id)
            print(f"User {user_id} finished with {machine_type.value}")
    finally:
        monitor.capacity.release()
        print(f"User {user_id} left the gym")
    
def spotter_thread():
    while True:
        with monitor._lock:
            monitor.spotter_available = True
            monitor.needs_spotter.notify()
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        # Start the spotter thread
        spotter = Thread(target=spotter_thread)
        spotter.start()

        # Start user manager thread
        user_manager_thread = Thread(target=user_manager)
        user_manager_thread.start()

        # Start user processor thread
        user_processor_thread = Thread(target=process_users)
        user_processor_thread.start()

        # Keep main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down gym...")
        running = False
        user_manager_thread.join(timeout=1)
        user_processor_thread.join(timeout=1)