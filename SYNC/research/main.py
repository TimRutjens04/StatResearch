from gym import *

# Example usage
monitor = Monitor(GymConfig())

def user_thread(user_id, routines, join_box = False):
    """Simulate a user working out with their preferred machines"""
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
    
def spotter_thread():
    while True:
        with monitor._lock:
            monitor.spotter_available = True
            monitor.needs_spotter.notify()
            time.sleep(0.1)

if __name__ == "__main__":
    # Create workout routines for different users
    workouts = [
        [MachineTypes.TREADMILL, MachineTypes.BENCH_PRESS],
        [MachineTypes.LEG_PRESS, MachineTypes.CALF_RAISE],
        [MachineTypes.CHEST_PRESS, MachineTypes.LAT_PULLDOWN],
        [MachineTypes.TREADMILL, MachineTypes.LEG_PRESS],
        [MachineTypes.BENCH_PRESS, MachineTypes.CHEST_PRESS],
    ]

    spotter = Thread(target=spotter_thread, daemon = True)
    spotter.start()

    # Create and start threads for 5 users
    threads = []
    for i in range(5):
        join_box = i < 3 #First 3 users join box class
        t = Thread(target=user_thread, args=(i, workouts[i], join_box))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Gym session completed!")