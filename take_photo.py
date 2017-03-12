#!/usr/bin/env python
'''Take a photo.

Take a photo using a USB or Raspberry Pi camera.
'''

import os.path, subprocess
from time import time, sleep


def image_filename():
    'Prepare filename with timestamp.'
    epoch = int(time())
    filename = '/tmp/images/{timestamp}.jpg'.format(timestamp=epoch)
    return filename

def usb_camera_photo():
    'Take a photo using a USB camera.'
    import cv2
    # Settings
    camera_port = 0      # default USB camera port
    discard_frames = 20  # number of frames to discard for auto-adjust

    # Check for camera
    if not os.path.exists('/dev/video' + str(camera_port)):
        print("No camera detected at video{}.".format(camera_port))
        camera_port += 1
        print("Trying video{}...".format(camera_port))
        if not os.path.exists('/dev/video' + str(camera_port)):
            print("No camera detected at video{}.".format(camera_port))

    # Open the camera
    camera = cv2.VideoCapture(camera_port)
    sleep(0.1)

    # Let camera adjust
    for _ in range(discard_frames):
        camera.grab()

    # Take a photo
    ret, image = camera.read()

    # Close the camera
    camera.release()

    # Output
    if ret:  # an image has been returned by the camera
        # Save the image to file
        cv2.imwrite(image_filename(), image)
        print("Image saved: {}".format(image_filename()))
    else:  # no image has been returned by the camera
        print("Problem getting image.")

def rpi_camera_photo():
    'Take a photo using the Raspberry Pi Camera.'
    from subprocess import call
    try:
        retcode = call(
            ["raspistill", "-w", "640", "-h", "480", "-o", image_filename()])
        if retcode == 0:
            print("Image saved: {}".format(image_filename()))
        else:
            print("Problem getting image.")
    except OSError:
        print("Raspberry Pi Camera not detected.")

if __name__ == '__main__':
    try:
        CAMERA = os.environ['camera']
    except (KeyError, ValueError):
        CAMERA = 'USB'  # default camera

    #for some rpi3, the rpi camera does not appear in os.environ, we use 
    # vcgencmd get_camera and check if the camera is plugged
    try:
        out=subprocess.check_output(['/opt/vc/bin/vcgencmd','get_camera'])
        dict=dict(s.split('=') for s in out.rstrip().split(' '))
        supported=dict['supported']
        detected=dict['detected']
    except:
        supported='0'
        detected='0'

    if 'RPI' in CAMERA or detected == '1':
        rpi_camera_photo()
    else:
        usb_camera_photo()
