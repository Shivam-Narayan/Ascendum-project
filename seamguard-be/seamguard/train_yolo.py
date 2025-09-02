import os
import yaml
# from ultralytics import YOLO
from .serializers import Annotation

def prepare_yolo_dataset(user, base_path='training_data'):
    user_folder = os.path.join(base_path, f"user_{user.id}")
    images_dir = os.path.join(user_folder, 'images')
    labels_dir = os.path.join(user_folder, 'labels')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    annotations = Annotation.objects.filter(user=user)

    classes = list(set(annotations.values_list('class_name', flat=True)))
    class_map = {name: idx for idx, name in enumerate(classes)}

    for ann in annotations:
        image_path = ann.image.image.path
        filename = os.path.basename(image_path)
        image_dest = os.path.join(images_dir, filename)
        label_dest = os.path.join(labels_dir, os.path.splitext(filename)[0] + '.txt')

        # Copy image
        if not os.path.exists(image_dest):
            import shutil
            shutil.copy(image_path, image_dest)

        # Write label file
        with open(label_dest, 'a') as f:
            x_center = (ann.x_min + ann.x_max) / 2
            y_center = (ann.y_min + ann.y_max) / 2
            width = ann.x_max - ann.x_min
            height = ann.y_max - ann.y_min
            f.write(f"{class_map[ann.class_name]} {x_center} {y_center} {width} {height}\n")

    # YAML file
    yaml_path = os.path.join(user_folder, 'data.yaml')
    with open(yaml_path, 'w') as f:
        yaml.dump({
            'train': images_dir,
            'val': images_dir,
            'nc': len(classes),
            'names': classes
        }, f)

    return yaml_path, user_folder
