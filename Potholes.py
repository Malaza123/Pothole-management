import RPi.GPIO as GPIO
import time
import subprocess
import requests
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE

# Set GPIO mode and pins
GPIO.setmode(GPIO.BCM)
TRIG_PIN = 17
ECHO_PIN = 18

# Set up the GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Initialize GPS
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

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

def capture_image(output_filename):
    try:
        # Run libcamera-still command with elevated privileges to capture an image
        subprocess.run(['sudo', 'libcamera-still', '-o', output_filename])
        print(f"Image captured and saved as {output_filename}")
    except Exception as e:
        print(f"Error capturing image: {e}")

def get_gps_coordinates():
    packet = gpsd.next()
    if packet['class'] == 'TPV':
        if hasattr(packet, 'lat') and hasattr(packet, 'lon'):
            return packet.lat, packet.lon
    return None, None

def main():
    try:
        while True:
            # Get distance (depth)
            depth = get_distance()
            print(f"Depth: {depth} cm")

            if depth > 15:  # Assuming a pothole depth threshold
                # Get GPS coordinates
                latitude, longitude = get_gps_coordinates()
                
                if latitude is not None and longitude is not None:
                    # Capture an image with an incremented filename
                    capture_image(f"pothole_{depth}_lat_{latitude}_lon_{longitude}.jpg")

                    # Send data to the API
                    api_url = "https://asapds.co.za/api/"
                    data = {'depth': depth, 'latitude': latitude, 'longitude': longitude}
                    files = {'image': open(f"pothole_{depth}_lat_{latitude}_lon_{longitude}.jpg", 'rb')}
                    response = requests.post(api_url, data=data, files=files)

                    if response.status_code == 200:
                        print("Data sent successfully")
                    else:
                        print("Error sending data. Status code:", response.status_code)

            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
