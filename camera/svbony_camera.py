import os
import time
import cv2
import numpy as np

try:
    import win32com.client  # For ASCOM
except ImportError:
    print("Warning: pywin32 not installed. ASCOM support may not work.")

try:
    import SVBCameraSDK  # Hypothetical SVBony SDK import, replace with real SDK import
except ImportError:
    print("Warning: SVBony SDK not installed. SDK support may not work.")


class SVBonyCamera:
    def __init__(self, use_ascom=True):
        """
        Initialize the camera handler.
        :param use_ascom: True to use ASCOM driver, False to use SVBony SDK.
        """
        self.use_ascom = use_ascom
        self.camera = None
        self.connected = False

    # ---------------- ASCOM DRIVER METHODS ---------------- #
    def connect_ascom_camera(self):
        """Connect to the camera using the ASCOM driver."""
        print("Connecting to camera via ASCOM...")
        self.camera = win32com.client.Dispatch("ASCOM.CameraDriver.Camera")
        self.camera.Connected = True
        self.connected = True
        print("ASCOM Camera connected successfully.")

    def set_ascom_settings(self, exposure, gain):
        """
        Set exposure and gain using ASCOM.
        :param exposure: Exposure time in seconds.
        :param gain: Gain value (if supported).
        """
        print(f"Setting ASCOM camera exposure: {exposure}s and gain: {gain}")
        self.camera.ExposureTime = exposure
        try:
            self.camera.Gain = gain  # Not all ASCOM drivers support Gain
        except AttributeError:
            print("Warning: ASCOM driver does not support gain adjustment.")

    def capture_ascom_image(self, output_file):
        """
        Capture an image using the ASCOM driver.
        :param output_file: Path to save the image.
        """
        print("Starting ASCOM exposure...")
        self.camera.StartExposure(self.camera.ExposureTime, False)
        while not self.camera.ImageReady:
            time.sleep(0.1)

        print("Exposure complete. Retrieving image...")
        image_array = self.camera.ImageArray
        image_data = np.array(image_array, dtype=np.uint16)
        cv2.imwrite(output_file, image_data)
        print(f"Image saved to {output_file}")

    # ---------------- SVBONY SDK METHODS ---------------- #
    def connect_sdk_camera(self):
        """Connect to the camera using the SVBony SDK."""
        print("Connecting to camera via SVBony SDK...")
        self.camera = SVBCameraSDK.Camera()  # Replace with real SDK camera object
        self.camera.open()
        self.connected = True
        print("SVBony SDK Camera connected successfully.")

    def set_sdk_settings(self, exposure, gain):
        """
        Set exposure and gain using the SVBony SDK.
        :param exposure: Exposure time in milliseconds.
        :param gain: Gain value.
        """
        print(f"Setting SDK camera exposure: {exposure}ms and gain: {gain}")
        self.camera.set_exposure(exposure)  # Replace with actual SDK method
        self.camera.set_gain(gain)         # Replace with actual SDK method

    def capture_sdk_image(self, output_file):
        """
        Capture an image using the SVBony SDK.
        :param output_file: Path to save the image.
        """
        print("Starting SDK exposure...")
        frame = self.camera.capture_frame()  # Replace with real SDK method
        if frame is not None:
            cv2.imwrite(output_file, frame)
            print(f"Image saved to {output_file}")
        else:
            print("Error: Failed to capture image from SDK camera.")

    # ---------------- UNIFIED INTERFACE ---------------- #
    def connect_camera(self):
        """Connect to the camera based on the selected driver."""
        if self.use_ascom:
            self.connect_ascom_camera()
        else:
            self.connect_sdk_camera()

    def configure_camera(self, exposure, gain):
        """
        Configure exposure and gain settings for the camera.
        :param exposure: Exposure time (seconds for ASCOM, milliseconds for SDK).
        :param gain: Gain value.
        """
        if not self.connected:
            raise ConnectionError("Camera not connected.")

        if self.use_ascom:
            self.set_ascom_settings(exposure, gain)
        else:
            self.set_sdk_settings(exposure, gain)

    def capture_image(self, output_file="captured_image.png"):
        """
        Capture an image and save it to a file.
        :param output_file: Path to save the image.
        """
        if not self.connected:
            raise ConnectionError("Camera not connected.")

        if self.use_ascom:
            self.capture_ascom_image(output_file)
        else:
            self.capture_sdk_image(output_file)

    def disconnect_camera(self):
        """Disconnect the camera."""
        if self.connected:
            if self.use_ascom:
                self.camera.Connected = False
            else:
                self.camera.close()  # Replace with actual SDK method
            print("Camera disconnected.")
        self.connected = False


# ---------------- MAIN PROGRAM ---------------- #
if __name__ == "__main__":
    use_ascom = True  # Set to False to use the SVBony SDK

    # Exposure time in seconds for ASCOM or milliseconds for SDK
    exposure_time = 2.0 if use_ascom else 2000  
    gain_value = 50

    camera_handler = SVBonyCamera(use_ascom=use_ascom)

    try:
        # Connect to the camera
        camera_handler.connect_camera()

        # Configure settings
        camera_handler.configure_camera(exposure=exposure_time, gain=gain_value)

        # Capture an image
        output_path = "svbony_captured_image.png"
        camera_handler.capture_image(output_file=output_path)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Disconnect the camera
        camera_handler.disconnect_camera()
