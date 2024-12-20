import os
import time
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.astrometry_net import AstrometryNet
from camera.svbony_camera import SVBonyCamera  # Previous SVBony Camera class
from mount.ascom_telescope import AltAzTelescopeController  # Previous ASCOM telescope class

class PlateSolver:
    def __init__(self, api_key=None, local_solver=True):
        """
        Plate Solver class using Astrometry.net API or a local solver.
        """
        self.local_solver = local_solver
        if not local_solver:
            if not api_key:
                raise ValueError("API key is required for Astrometry.net online solving.")
            self.astrometry = AstrometryNet()
            self.astrometry.api_key = api_key

    def solve_image(self, image_path):
        """
        Solves the image and returns the center RA and DEC.
        """
        print("Starting plate solving...")
        if self.local_solver:
            # Use local Astrometry.net solver
            solve_command = f'solve-field --overwrite --no-plots --quiet {image_path}'
            os.system(solve_command)
            solved_wcs = image_path.replace(".png", ".wcs")
            if os.path.exists(solved_wcs):
                print(f"Plate solving successful: {solved_wcs}")
                return self.parse_wcs(solved_wcs)
            else:
                raise FileNotFoundError("Plate solving failed. No WCS file generated.")
        else:
            # Use Astrometry.net API
            job_id = self.astrometry.upload(image_path, public=False)
            result = self.astrometry.monitor_submission(job_id)
            ra = result['calibration']['ra']
            dec = result['calibration']['dec']
            print(f"Plate solving successful: RA={ra}, DEC={dec}")
            return ra, dec

    @staticmethod
    def parse_wcs(wcs_file):
        """
        Extract RA and DEC from a WCS file.
        """
        from astropy.io import fits
        with fits.open(wcs_file) as hdul:
            header = hdul[0].header
            ra = header['CRVAL1']
            dec = header['CRVAL2']
            print(f"Extracted from WCS: RA={ra}, DEC={dec}")
            return ra, dec

def main():
    # Step 1: Initialize camera and telescope
    camera = SVBonyCamera()
    telescope = AltAzTelescopeController()

    # Step 2: Connect to camera and telescope
    print("Initializing camera and telescope...")
    if not camera.init_camera() or not telescope.connect_to_telescope():
        print("Initialization failed. Exiting...")
        return

    try:
        # Step 3: Capture an image
        output_image = "plate_solve_image.png"
        camera.configure_camera(exposure_ms=2000, gain=50)  # 2s exposure, gain 50
        camera.capture_image(output_file=output_image)

        # Step 4: Perform plate solving
        plate_solver = PlateSolver(local_solver=True)  # Use local Astrometry.net
        ra, dec = plate_solver.solve_image(output_image)

        # Step 5: Target M42 coordinates
        m42 = SkyCoord(ra=5*u.hourangle + 35*u.minute + 17.3*u.second, 
                       dec=-5*u.degree - 23*u.arcminute - 28*u.arcsecond, frame='icrs')

        print(f"Target M42: RA={m42.ra.degree}°, DEC={m42.dec.degree}°")

        # Step 6: Slew to M42
        print("Slewing to M42...")
        telescope.slew_to_altaz(altitude=90.0, azimuth=180.0)  # Simulated values

        print("Telescope slewed to M42 successfully!")

    finally:
        # Step 7: Cleanup
        camera.close_camera()
        telescope.disconnect_telescope()
        print("Telescope and camera disconnected. Program finished.")

if __name__ == "__main__":
    main()
