import platform
import sys
import RPi.GPIO as GPIO
import time
import requests

# Check if running on Raspberry Pi
if platform.system() != 'Linux' or platform.machine() not in ('armv7l', 'armv6l', 'aarch64'):
    print("This script should be run on a Raspberry Pi.")
    sys.exit(1)

# Set GPIO mode and pins
GPIO.setmode(GPIO.BCM)
TRIG_PIN = 17
ECHO_PIN = 18

# Set up the GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
    # Trigger pulse
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # Initialize variables
    pulse_start = time.time()
    pulse_end = pulse_start

    # Measure the time it takes for the echo to go high
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    # Calculate distance in centimeters
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def main():
    try:
        while True:
            distance = get_distance()
            print(f"Distance: {distance} cm")

            if distance > 25:
                # Send data to the API
                api_url = "https://asapds.co.za/api/?distance={}".format(distance)
                response = requests.get(api_url)

                if response.status_code == 200:
                    print("Data sent successfully")
                else:
                    print("Error sending data. Status code:", response.status_code)

            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
