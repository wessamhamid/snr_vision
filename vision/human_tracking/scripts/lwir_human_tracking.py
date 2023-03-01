#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

class MediaPipeHumanTrackingNode:
  def __init__(self):
    self.bridge = CvBridge()
    rospy.Subscriber("/seek_thermal_image", Image, self.image_callback)
    self.publisher = rospy.Publisher("/lwir/human_tracking", Image, queue_size=1)

  def image_callback(self, data):
    try:
      image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_holistic.Holistic(
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as holistic:
      results = holistic.process(image)

    # Draw landmark annotation on the image.
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.face_landmarks,
        mp_holistic.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_contours_style())
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_holistic.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles
        .get_default_pose_landmarks_style())

    try:
      self.publisher.publish(self.bridge.cv2_to_imgmsg(image, "bgr8"))
    except CvBridgeError as e:
      print(e)

if __name__ == '__main__':
  rospy.init_node('lwir_human_tracking')
  node = MediaPipeHumanTrackingNode()
  rospy.spin()