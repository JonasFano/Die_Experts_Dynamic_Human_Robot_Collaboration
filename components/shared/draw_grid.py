import cv2 

def draw_grid(image, width, height, spacing=20):
    
    width_list = list(range(0, width, spacing))
    height_list = list(range(0, height, spacing))
    spacing_divid = int(spacing/3)

    text_color = (0, 120, 120)
    
    for i, coord in enumerate(width_list):
        cv2.line(image, (coord, 0), (coord, height), (255,255,0), 2)
        cv2.putText(image, f"{coord}", (coord+spacing_divid, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.3, text_color, 1, cv2.LINE_AA)
        
    for i, coord in enumerate(height_list):
        cv2.line(image, (0, coord), (width, coord), (255,255,0), 2)
        cv2.putText(image, f"{coord}", (20, coord+spacing_divid),
            cv2.FONT_HERSHEY_SIMPLEX, 0.3, text_color, 1, cv2.LINE_AA)