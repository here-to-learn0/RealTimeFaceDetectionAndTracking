import os
import yaml
import numpy as np
import time
import torch

def load_cfg(name):
    path = os.path.join("configs", name)
    with open(path, 'r') as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data

def check_fps(begin_time):
    execution_time = time.time() - begin_time
    fps = np.around(1/ execution_time, 2)
    return fps

def resize_img(frame_shape):
    org_h, org_w = frame_shape[:2]
    w, h = 320, 240 
    dim = (w, h)
    scaling_factor = org_w // w

    return dim, scaling_factor

def get_centeroids(tracks):
    mean_x = np.mean(tracks[:, [0, 2]], axis=1)
    mean_y = np.mean(tracks[:, [1, 3]], axis=1)
    return np.concatenate((mean_x.reshape(-1, 1), mean_y.reshape(-1, 1)), axis=1)

def leftmost_n(tracks, num_persons_to_track):
    if num_persons_to_track > len(tracks):
        # print(num_persons_to_track, len(tracks))
        print("People detected less than people to be tracked, increase people fast")
        return None, None

    else:
        centeriods = get_centeroids(tracks)
        left_most_ids =  np.argsort(centeriods[:, 0])[:num_persons_to_track]
        return left_most_ids, centeriods[left_most_ids]

def find_mean_point(centroids):
    if centroids is None:
        return 
    else:
        # print(centroids)
        # print(np.mean(centroids, axis=0))
        return np.mean(centroids, axis=0)

def load_classes_dict(path):
    classes_list = np.loadtxt(path, dtype=str)
    int2labels = {int(label):cls for label, cls in classes_list}
    return int2labels

def get_cropped_faces(detections, frame, transform):
    cropped_imges = []
    if len(detections) == 1:
        det = detections[0]
        det = det.astype(int)
        boxes, _ = det[:4], det[4]
        cropped_img = frame[boxes[1]:boxes[3], boxes[0]: boxes[2], :]
        cropped_img = transform(cropped_img)
        return cropped_img.unsqueeze(0)
    for det in detections:
        det = det.astype(int)
        boxes, _ = det[:4], det[4]
        cropped_img = frame[boxes[1]:boxes[3], boxes[0]: boxes[2], :]
        cropped_img = transform(cropped_img)
        cropped_imges.append(cropped_img.unsqueeze(0))
    return torch.cat(cropped_imges)