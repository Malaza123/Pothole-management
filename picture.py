import subprocess

def capture_image(output_filename):
    try:
        # Run libcamera-still command with elevated privileges to capture an image
        subprocess.run(['sudo', 'libcamera-still', '-o', output_filename])

        print(f"Image captured and saved as {output_filename}")
    except Exception as e:
        print(f"Error capturing image: {e}")

def open_camera():
    output_filename = "test.jpg"

    print("Press 'Enter' to capture an image. Type 'exit' and press 'Enter' to exit.")
    try:
        while True:
            # Wait for the user to press 'Enter'
            input_str = input()
            
            if input_str.lower() == 'exit':
                break
            
            # Capture an image
            capture_image(output_filename)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing camera.")

if __name__ == "__main__":
    open_camera()
