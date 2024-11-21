from .safety_minitor import SafetyFrameResults, SafetyMonitor, PATCH_COORDS_LIST
import Queue


def DistanceJob(s: SafetyFrameResults, q: Queue) -> None:
    poses = SafetyMonitor.calculate_poses(s.color_image)
    distance = SafetyMonitor.calculate_human_robot_distance(
        poses, s.color_frame, s.color_image
    )
    q.put(distance)


def ImageStreamJob(s: SafetyFrameResults, q: Queue) -> None:
    # Copy the image array to ensure no race condition/mutation errors
    color_image = s.color_image.copy()
    poses = SafetyMonitor.calculate_poses(color_image)
    SafetyMonitor.apply_landmark_overlay(color_image, poses)
    SafetyMonitor.apply_some_graphic(s.color_image, PATCH_COORDS_LIST)
    q.put(s.color_image)
