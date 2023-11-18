import subprocess
import keyboard  # You may need to install this library using: pip install keyboard

def capture_image(output_filename):
    try:
        # Run libcamera-still command with elevated privileges to capture an image
        subprocess.run(['sudo', 'libcamera-still', '-o', output_filename])

        print(f"Image captured and saved as {output_filename}")
    except Exception as e:
        print(f"Error capturing image: {e}")

def open_camera():
    output_filename = "test.jpg"

    print("Camera is open. Press 'q' to exit.")
    try:
        while True:
            # Capture an image
            capture_image(output_filename)

            # Wait for a key press ('q' to exit)
            if keyboard.is_pressed('q'):
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing camera.")

if __name__ == "__main__":
    open_camera()
