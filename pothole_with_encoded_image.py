import RPi.GPIO as GPIO
import time
import subprocess
import requests
import base64

# Set GPIO mode and pins
GPIO.setmode(GPIO.BCM)
TRIG_PIN = 17
ECHO_PIN = 18

# Set up the GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

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
        # Run libcamera-still command with elevated privileges to capture an image
        subprocess.run(['sudo', 'libcamera-still', '-o', f"{IMAGE_FOLDER}/{output_filename}"])
        print(f"Pothole captured and saved as {output_filename}")
    except Exception as e:
        print(f"Error capturing pothole: {e}")

def save_data_to_file(filename, distance, image_filename):
    with open(f"{IMAGE_FOLDER}/{image_filename}", 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')

    with open(filename, 'a') as file:
        file.write(f"Depth: {distance} cm, Image: {image_filename}\n")

    return base64_encoded

def send_data_to_api(api_url, distance, base64_image, image_filename):
    data = {'depth': distance, 'image': base64_image}
    files = {'image': open(f"{IMAGE_FOLDER}/{image_filename}", 'rb')}

    try:
        response = requests.post(api_url, data=data, files=files)
        print(f"API Response: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error sending data to the API: {e}")

def main():
    try:
        while True:
            distance = get_distance()
            print(f"Depth: {distance} cm")

            if distance > 25:
                # Capture an image
                image_filename = f"pothole_{int(time.time())}.jpg"  # Using timestamp as the image filename
                capture_image(image_filename)

                # Save data to local file and get base64 encoded image
                base64_image = save_data_to_file("pothole_data.txt", distance, image_filename)

                # Send data to the API
                api_url = "https://asapds.co.za/api/"
                send_data_to_api(api_url, distance, base64_image, image_filename)

            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
