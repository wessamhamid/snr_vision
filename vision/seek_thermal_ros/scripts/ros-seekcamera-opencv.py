#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from threading import Condition
import cv2
import numpy as np
from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCamera,
    SeekFrame,
)

class Renderer:
    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True

def on_frame(_camera, camera_frame, renderer):
    with renderer.frame_condition:
        renderer.frame = camera_frame.color_argb8888
        renderer.frame_condition.notify()

def on_event(camera, event_type, event_status, renderer):
    print("{}: {}".format(str(event_type), camera.chipid))
    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return
        renderer.busy = True
        renderer.camera = camera
        renderer.first_frame = True

        # "BLACK_HOT" color palette gives more accurate results for human skeletal tracking
        camera.color_palette = SeekCameraColorPalette.TYRIAN
        # camera.color_palette = SeekCameraColorPalette.BLACK_HOT
        camera.register_frame_available_callback(on_frame, renderer)
        camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        if renderer.camera == camera:
            camera.capture_session_stop()
            renderer.camera = None
            renderer.frame = None
            renderer.busy = False

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return

def main():
    rospy.init_node("seek_thermal_publisher", anonymous=True)
    pub = rospy.Publisher("seek_thermal_image", Image, queue_size=1)
    bridge = CvBridge()
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)
        while not rospy.is_shutdown():
            with renderer.frame_condition:
                if renderer.frame_condition.wait(150.0 / 1000.0):
                    img = renderer.frame.data

                    # Resize the rendering window.
                    if renderer.first_frame:
                        (height, width, _) = img.shape
                        renderer.first_frame = False

                    #Uncomment to use thermal human skeletal tracking:
                    # img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                    # ros_image = bridge.cv2_to_imgmsg(img, encoding="bgr8")

                    #Comment to use thermal human skeletal tracking:
                    ros_image = bridge.cv2_to_imgmsg(img, encoding="8UC4")

                    pub.publish(ros_image)
            # Process key events.
            key = cv2.waitKey(1)
            if key == ord("q"):
                break


if __name__ == "__main__":
    main()