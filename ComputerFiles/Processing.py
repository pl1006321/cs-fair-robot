import cv2
import numpy as np
import time
import requests

# Functions that use the basic OpenCv functions to help detect things within the image
def apply_gaussian_blur(image, kernel_size=(9, 9)):
    return cv2.GaussianBlur(image, kernel_size, 0)

def canny_edge_detection(image, low_threshold=150, high_threshold=200):
    return cv2.Canny(image, low_threshold, high_threshold)

def dilate_with_buffer(image, buffer_radius=5):
    kernel = np.ones((buffer_radius, buffer_radius), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)

def hsv_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    masked = cv2.bitwise_and(frame, frame, mask=mask)

    return masked


def detect_centerline(image, orientation="vertical", buffer_radius=5):
    blue_segmented= hsv_mask(image)
    gray = cv2.cvtColor(blue_segmented, cv2.COLOR_BGR2GRAY)
    blurred = apply_gaussian_blur(gray)
    edges = canny_edge_detection(blurred)
    dilated_edges = dilate_with_buffer(edges, buffer_radius)

    line_image = image.copy()

    lines = cv2.HoughLinesP(dilated_edges, 1, np.pi / 180, 100, minLineLength=80, maxLineGap=10)
    if lines is not None:
        relevant_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if orientation == "vertical" and abs(x2 - x1) < abs(y2 - y1):
                relevant_lines.append(((x1 + x2) // 2, abs(y2 - y1)))
            elif orientation == "horizontal" and abs(y2 - y1) < abs(x2 - x1):
                relevant_lines.append(((y1 + y2) // 2, abs(x2 - x1)))

        if relevant_lines:
            if orientation == "vertical":
                weighted_sum = sum(x * length for x, length in relevant_lines)
                total_length = sum(length for _, length in relevant_lines)
                center_x = int(weighted_sum / total_length) if total_length > 0 else image.shape[1] // 2
                cv2.line(line_image, (center_x, 0), (center_x, line_image.shape[0]), (0, 0, 255), 2)
            elif orientation == "horizontal":
                weighted_sum = sum(y * length for y, length in relevant_lines)
                total_length = sum(length for _, length in relevant_lines)
                if total_length > 0:
                    center_y = int(weighted_sum / total_length)
                else:
                    center_y = image.shape[0] // 2
                cv2.line(line_image, (0, center_y), (line_image.shape[1], center_y), (0, 0, 255), 2)

    return line_image

# Resize function to ensure all frames are the same size
def resize_frame(frame):
    return cv2.resize(frame, (1280, 720))

# Function to detect orientation of lines (horizontal or vertical)
def detect_lines_orientation(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = canny_edge_detection(gray)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

    vertical_lines = 0
    horizontal_lines = 0

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x2 - x1) < abs(y2 - y1):
                vertical_lines += 1
            elif abs(y2 - y1) < abs(x2 - x1):
                horizontal_lines += 1

    if vertical_lines > horizontal_lines:
        return "vertical"
    else:
        return "horizontal"

# Function to draw parallel lines (vertical or horizontal) on the image
def draw_parallel_lines(image, orientation="vertical"):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = apply_gaussian_blur(gray)
    edges = canny_edge_detection(blurred)
    dilated_edges = dilate_with_buffer(edges)

    line_image = image.copy()

    lines = cv2.HoughLinesP(dilated_edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if orientation == "vertical" and abs(x2 - x1) < abs(y2 - y1):
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw green for vertical lines
            elif orientation == "horizontal" and abs(y2 - y1) < abs(x2 - x1):
                cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw blue for horizontal lines

    return line_image

def post_direction(direction='forward'):
    try:
        url = 'http://192.168.240.22:5000/'
        endpoint = url + 'moving'
        data = {'direction': direction}
        req = requests.post(endpoint, json=data)
    except Exception as e:
        print(f'error: {e}')

# def apply_overlay(frame, movement_queue):
#     new = frame.copy()
#     cropped = new[130:170, :]
#     blurred = apply_gaussian_blur(cropped)
#     masked = hsv_mask(blurred)

#     orientation = detect_lines_orientation(masked)
    
#     if orientation == 'horizontal':
#         processed_frame = draw_parallel_lines(masked, orientation="horizontal")
#         processed_frame = detect_centerline(masked, orientation="horizontal")

#         movement_queue.put(('horizontal_line_detected', None))

#     else:
#         processed_frame = draw_parallel_lines(masked, orientation="vertical")
#         processed_frame = detect_centerline(masked, orientation="vertical")

#     new[130:170, :] = processed_frame
#     cv2.rectangle(new, (0, 130), (400, 170), (255, 0, 255), 2)

#     return new, orientation

def apply_overlay(frame):
    return frame
