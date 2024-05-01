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

def measure_distance():
    """Trigger ultrasonic sensor and return the measured distance."""
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    
    StopTime = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    
    TimeElapsed = StopTime - StartTime
    return (TimeElapsed * 34300) / 2  # Calculate distance in centimeters

def write_to_csv(index, date_time, milliseconds, detections):
    """Write detection data to a CSV file."""
    with open('people_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([index, date_time, milliseconds, detections])

def main():
    people_count = 0
    detections_within_interval = 0
    start_time = time.time()
    csv_index = 0  # To keep track of each entry's index

    # Create or overwrite the CSV file with headers
    with open('people_log.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Date and Time", "Time in Milliseconds", "Detections per Person"])
    
    print("Starting distance measurement...")

    try:
        while True:
            dist = measure_distance()
            print(f"Measured Distance = {dist} cm")
            if dist < 100:  # Assuming an object is detected within 100 cm
                detections_within_interval += 1

            current_time = time.time()
            # Check if it's time to log the detections
            if current_time - start_time >= 1800:  # 30 minutes
                if detections_within_interval > 0:
                    people_count += detections_within_interval
                    print(f"People count: {people_count}")
                    current_milliseconds = int((current_time - start_time) * 1000)
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