import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime

# Set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Set GPIO direction (IN / OUT)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    
    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    
    # Time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # Multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    
    return distance

def write_to_csv(index, date_time, milliseconds, detections):
    with open('people_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([index, date_time, milliseconds, detections])

def main():
    people_count = 0
    detections_within_interval = 0
    start_time = time.time()
    csv_index = 0  # To keep track of each entry's index
    last_saved_time = time.time()  # Initialize the last saved time
    
    # Create or overwrite the CSV file with headers
    with open('people_log.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Date and Time", "Time in Milliseconds", "Detections per Person"])
    
    try:
        while True:
            current_time = time.time()
            if current_time - start_time >= 1:
                dist = distance()
                print(f"Measured Distance = {dist} cm")
                if dist < 100:  # Assuming an object is detected within 100 cm
                    detections_within_interval += 1
                # Log to CSV every 30 minutes
                if current_time - last_saved_time >= 1800:
                    if detections_within_interval > 0:  # If there were detections within the interval
                        people_count += 1
                        print(f"People count: {people_count}")
                        # Log to CSV
                        current_milliseconds = int((current_time - last_saved_time) * 1000)
                        write_to_csv(csv_index, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_milliseconds, detections_within_interval)
                        csv_index += 1
                    # Reset for the next interval
                    detections_within_interval = 0
                    last_saved_time = current_time
                time.sleep(0.05)  # Short sleep to reduce CPU load
    
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

if __name__ == '__main__':
    main()

