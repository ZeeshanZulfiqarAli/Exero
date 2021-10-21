import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
import glob
import xml.etree.ElementTree as ET
import time

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from object_detection.utils import ops as utils_ops


# This is needed to display the images.
#%matplotlib inline



#PATH_TO_CKPT = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_20000epochs\\frozen_inference_graph.pb"
#PATH_TO_CKPT = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_25000epochs_dropout90\\2_frozen_inference_graph.pb"
#PATH_TO_CKPT = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_12613epochs_dropout90_autoaugment\\3_frozen_inference_graph.pb"
#PATH_TO_CKPT = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_14556+25000epochs_dropout90_autoaugment_lr0.004_step2000_rate95\\4(2)_frozen_inference_graph.pb"
PATH_TO_CKPT = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_25000epochs_adam_dropout90_autoaugment_lr0.004_step2000_decayRate95\\5_frozen_inference_graph.pb"
PATH_TO_LABELS = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_20000epochs_rmsProp_lr0.004\\my_label_map.pbtxt"
PATH_TO_TEST_VID = "D:\\assignments\\fyp\\WL.mp4"
PATH_TO_OUTPUT_VID = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_25000epochs_adam_dropout90_autoaugment_lr0.004_step2000_decayRate95\\"
path = "D:\\assignments\\fyp\\Kvasir-SEG\\test_xml\\" #xml path
num_classes = 1

print(os.path.exists(PATH_TO_CKPT))
'''print(os.path.isdir(TEST_IMAGE_PATHS))
print(os.path.isdir(path))
print(os.path.isfile(PATH_TO_LABELS))'''
#os.path.exists()




#print("11111")
from object_detection.utils import label_map_util
#print("22222")
from object_detection.utils import visualization_utils as vis_util
#print("33333")

detection_graph = tf.Graph()
#print("44444")
with detection_graph.as_default():
    
    od_graph_def = tf.GraphDef()

    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=num_classes, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

print("55555")

def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.Session() as sess:
            # Get handles to input and output tensors
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {
                output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                        tensor_name)
            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(
                    tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(
                    tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                real_num_detection = tf.cast(
                    tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [
                                           real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [
                                           real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image.shape[0], image.shape[1])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            # Run inference
            output_dict = sess.run(tensor_dict,
                                   feed_dict={image_tensor: np.expand_dims(image, 0)})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(
                output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                'detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict

cap = cv2.VideoCapture(PATH_TO_TEST_VID)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
out = cv2.VideoWriter(PATH_TO_OUTPUT_VID+'output.avi',fourcc,cap.get(cv2.CAP_PROP_FPS),(int(width),int(height)))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        #image_np_expanded = np.expand_dims(frame, axis=0)
        # Actual detection.
        t1 = time.time()
        output_dict = run_inference_for_single_image(frame, detection_graph)
        t2 = time.time() - t1
        print("t2: ",t2)
        # Visualization of the results of a detection.
        t1 = time.time()
        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            category_index,
            instance_masks=output_dict.get('detection_masks'),
            use_normalized_coordinates=True,
            line_thickness=8)
        # write the flipped frame
        print("vis time: ",time.time()-t1)
        out.write(frame)
    else:
        break

#  Release everything if job is finished
print("done")
cap.release()
out.release()
#cv2.destroyAllWindows()
    