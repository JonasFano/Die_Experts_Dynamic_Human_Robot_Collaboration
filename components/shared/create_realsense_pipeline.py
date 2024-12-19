import pyrealsense2 as rs

def create_pipeline():
    pipeline = rs.pipeline()
    config = rs.config()
    align_to = rs.stream.color
    align = rs.align(align_to)
    pipeline.start(config)
    return (pipeline, align)