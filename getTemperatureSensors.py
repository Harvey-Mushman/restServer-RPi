# # getTemperatureSensors.py

# import glob
# import time
# import threading

# # Global cache variables
# cached_temperatures = []
# last_update = 0
# update_interval = 60  # Cache update interval in seconds

# # Function to read temperature from a single DS18B20 sensor
# def read_sensor(sensor_id):
#     try:
#         with open(f"/sys/bus/w1/devices/{sensor_id}/w1_slave") as file:
#             content = file.read()
#         if "YES" not in content.split("\n")[0]:
#             return {"sensor": sensor_id, "value": None}
#         temp_str = content.split("\n")[1].split(" ")[9][2:]
#         temp_c = float(temp_str) / 1000.0
#         return {"sensor": sensor_id, "value": temp_c * 9 / 5 + 32}
#     except Exception as e:
#         return {"sensor": sensor_id, "value": None, "error": str(e)}

# # # Function to read all temperatures (live)
# # def read_all_temperatures():
# #     sensor_paths = glob.glob("/sys/bus/w1/devices/28-*")
# #     print(f"Detected sensors: {sensor_paths}")
# #     sensor_ids = [path.split("/")[-1] for path in sensor_paths]
# #     results = []
# #     for sensor_id in sensor_ids:
# #         result = read_sensor(sensor_id)
# #         print(f"Read sensor {sensor_id}: {result}")
# #         results.append(result)
# #     return results

# # Function to update the temperature cache
# DEBUG = False  # Set to True to enable detailed logging

# # Function to update the temperature cache
# def update_cache():
#     global cached_temperatures, last_update
#     while True:
#         try:
#             start_time = time.time()
#             cached_temperatures = read_all_temperatures()
#             last_update = time.time()
#             print(f"Cache updated in {last_update - start_time:.2f} seconds")
#             if DEBUG:
#                 print(f"Cached Temperatures: {cached_temperatures}")
#         except Exception as e:
#             print(f"Error updating cache: {e}")
#         time.sleep(update_interval)

# # Function to read all temperatures
# def read_all_temperatures():
#     sensor_paths = glob.glob("/sys/bus/w1/devices/28-*")
#     sensor_ids = [path.split("/")[-1] for path in sensor_paths]
#     results = []
#     for sensor_id in sensor_ids:
#         result = read_sensor(sensor_id)
#         if DEBUG:
#             print(f"Read sensor {sensor_id}: {result}")
#         results.append(result)
#     return results

# # Start cache updater in a background thread
# threading.Thread(target=update_cache, daemon=True).start()

import glob
import time
import threading

# Global cache variables
cached_temperatures = []
last_update = 0
update_interval = 60  # Cache update interval in seconds
cache_lock = threading.Lock()  # Lock for synchronizing access to cache

# Function to read temperature from a single DS18B20 sensor
def read_sensor(sensor_id):
    try:
        with open(f"/sys/bus/w1/devices/{sensor_id}/w1_slave") as file:
            content = file.read()
        if "YES" not in content.split("\n")[0]:
            return {"sensor": sensor_id, "value": None}
        temp_str = content.split("\n")[1].split(" ")[9][2:]
        temp_c = float(temp_str) / 1000.0
        return {"sensor": sensor_id, "value": temp_c * 9 / 5 + 32}
    except Exception as e:
        return {"sensor": sensor_id, "value": None, "error": str(e)}

# Function to read all temperatures
def read_all_temperatures():
    sensor_paths = glob.glob("/sys/bus/w1/devices/28-*")
    sensor_ids = [path.split("/")[-1] for path in sensor_paths]
    results = []
    for sensor_id in sensor_ids:
        result = read_sensor(sensor_id)
        results.append(result)
    return results

# Function to update the temperature cache
def update_cache():
    global cached_temperatures, last_update
    while True:
        try:
            start_time = time.time()
            new_temperatures = read_all_temperatures()
            if new_temperatures:
                with cache_lock:
                    cached_temperatures = new_temperatures
                    last_update = time.time()
                print(f"Cache updated successfully at {time.ctime(last_update)} with {len(cached_temperatures)} sensors.")
            else:
                print("Warning: read_all_temperatures returned no data.")
        except Exception as e:
            print(f"Error updating cache: {e}")
        time.sleep(update_interval)

# Getter function to safely retrieve cached temperatures
def get_cached_temperatures():
    with cache_lock:
        return cached_temperatures
    
# Getter function to safely retrieve last update time
def get_last_update():
    with cache_lock:
        return last_update


# Start cache updater in a background thread
threading.Thread(target=update_cache, daemon=True).start()
