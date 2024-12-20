import time
import win32com.client

class AltAzTelescopeController:
    def __init__(self):
        """Initialize the ASCOM telescope controller."""
        self.telescope = None

    def connect_to_telescope(self):
        """Connect to the telescope via ASCOM Chooser."""
        try:
            print("Opening ASCOM Chooser...")
            chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
            chooser.DeviceType = "Telescope"

            # Let the user pick the telescope driver
            telescope_driver = chooser.Choose(None)
            if not telescope_driver:
                print("No telescope selected. Exiting.")
                return False

            # Connect to the telescope
            print(f"Connecting to telescope: {telescope_driver}")
            self.telescope = win32com.client.Dispatch(telescope_driver)

            if not self.telescope.Connected:
                self.telescope.Connected = True

            print("Telescope connected successfully.")
            return True
        except Exception as e:
            print(f"Error connecting to telescope: {e}")
            return False

    def slew_to_altaz(self, altitude, azimuth):
        """
        Slew the telescope to the specified altitude and azimuth.

        Args:
            altitude (float): The altitude in degrees.
            azimuth (float): The azimuth in degrees.
        """
        try:
            print(f"Slewing to Altitude: {altitude}°, Azimuth: {azimuth}°...")
            self.telescope.SlewToAltAz(azimuth, altitude)

            # Monitor slewing status
            while self.telescope.Slewing:
                print("Telescope is slewing...")
                time.sleep(1)

            print("Slew complete.")
        except Exception as e:
            print(f"Error during slew: {e}")

    def disconnect_telescope(self):
        """Disconnect the telescope."""
        if self.telescope and self.telescope.Connected:
            print("Disconnecting telescope...")
            self.telescope.Connected = False
            print("Telescope disconnected.")

if __name__ == "__main__":
    controller = AltAzTelescopeController()

    # Connect to the telescope
    if controller.connect_to_telescope():
        try:
            # Example: Slew to Altitude 45°, Azimuth 90°
            controller.slew_to_altaz(altitude=45.0, azimuth=90.0)

        finally:
            # Disconnect the telescope
            controller.disconnect_telescope()
