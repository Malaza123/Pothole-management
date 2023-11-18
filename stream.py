import RPi.GPIO as GPIO
import time
import subprocess
import requests
from picamera import PiCamera

# Disable GPIO warnings
GPIO.setwarnings(False)

# Set GPIO mode and pins
GPIO.setmode(GPIO.BCM)
TRIG_PIN = 17
ECHO_PIN = 18

# Set up the GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Initialize GPS
gpsd = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)

# Create a folder to store images
IMAGE_FOLDER = "images"
subprocess.run(["mkdir", "-p", IMAGE_FOLDER])

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
        # Use the PiCamera to capture an image
        with PiCamera() as camera:
            camera.capture(f"{IMAGE_FOLDER}/{output_filename}")
        print(f"Pothole captured and saved as {output_filename}")
    except Exception as e:
        print(f"Error capturing pothole: {e}")

def get_gps_coordinates():
    packet = gpsd.next()
    if packet['class'] == 'TPV':
        if hasattr(packet, 'lat') and hasattr(packet, 'lon'):
            return packet.lat, packet.lon
    return None, None

def save_data_to_file(filename, depth, latitude, longitude, image_filename):
    with open(filename, 'a') as file:
        file.write(f"Depth: {depth} cm, Latitude: {latitude}, Longitude: {longitude}, Image: {image_filename}\n")

def main():
    try:
        while True:
            # Get distance (depth)
            distance = get_distance()
            print(f"Depth: {distance} cm")

            if distance > 25:
                # Get GPS coordinates
                latitude, longitude = get_gps_coordinates()
                
                if latitude is not None and longitude is not None:
                    # Capture an image with a timestamp as the filename
                    image_filename = f"pothole_{int(time.time())}.jpg"
                    capture_image(image_filename)

                    # Save data to local file
                    save_data_to_file("pothole_data.txt", distance, latitude, longitude, image_filename)

                    # Send data to the API
                    api_url = "https://asapds.co.za/api/"
                    data = {'depth': distance, 'latitude': latitude, 'longitude': longitude}
                    files = {'image': open(f"{IMAGE_FOLDER}/{image_filename}", 'rb')}
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
