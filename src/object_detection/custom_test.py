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
PATH_TO_CKPT = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_25000epochs_dropout90\\2_frozen_inference_graph.pb"
PATH_TO_LABELS = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_20000epochs\\my_label_map.pbtxt"
PATH_TO_TEST_IMAGES_DIR = "D:\\assignments\\fyp\\Kvasir-SEG\\test"
path = "D:\\assignments\\fyp\\Kvasir-SEG\\test_xml\\" #xml path
#PATH_TO_SAVE_IMG_OUT = "D:/TensorFlow/workspace/fyp_ssd_inception_v2_20000epochs/"
PATH_TO_SAVE_IMG_OUT = "D:/TensorFlow/workspace/fyp_ssd_inception_v2_25000epochs_dropout90/"
num_classes = 1

TEST_IMAGE_PATHS = glob.glob(os.path.join(PATH_TO_TEST_IMAGES_DIR, "*.*"))
assert len(TEST_IMAGE_PATHS) > 0, 'No image found in `{}`.'.format(PATH_TO_TEST_IMAGES_DIR)
print(TEST_IMAGE_PATHS)

print(os.path.exists(PATH_TO_CKPT))
'''print(os.path.isdir(TEST_IMAGE_PATHS))
print(os.path.isdir(path))
print(os.path.isfile(PATH_TO_LABELS))'''
#os.path.exists()
print("11111")
from object_detection.utils import label_map_util
print("22222")
from object_detection.utils import visualization_utils as vis_util
print("33333")

detection_graph = tf.Graph()
print("44444")
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
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)


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

#path = '/gdrive/My Drive/Kvasir-SEG/test_xml/'
for image_path in TEST_IMAGE_PATHS:
    img_name = image_path.split('\\')[-1]
#    print(img_name)
#    if img_name != 'cju1cu1u2474n0878tt7v4tdr.jpg':
#        continue
    tree = ET.parse(path+img_name[:-4]+'.xml')
    
    ground_truth = []
#    print(ground_truth)
    for obj in tree.findall("object"):
        xmin= int(obj.find("bndbox").find("xmin").text)
        ymin= int(obj.find("bndbox").find("ymin").text)
        xmax= int(obj.find("bndbox").find("xmax").text)
        ymax= int(obj.find("bndbox").find("ymax").text)
        ground_truth.append(np.array([ymax,xmin,ymin,xmax]))
        #ground_truth = np.append(ground_truth,np.array([np.array([ymax,xmin,ymin,xmax])]),axis=0)
    ground_truth = np.array(ground_truth,dtype = 'float32')
    image = Image.open(image_path)
#    print(ground_truth)
#    print(ground_truth.shape)
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    org_image_np = image_np.copy()
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    t1 = time.time()
    output_dict = run_inference_for_single_image(image_np, detection_graph)
    t2 = time.time() - t1
    print("t2: ",t2)
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks'),
        use_normalized_coordinates=True,
        line_thickness=8)
#    print(output_dict['detection_scores'].dtype)
#    print(type(output_dict['detection_scores']))
#    print(np.ones(ground_truth.shape[0]))
#    print(np.ones(ground_truth.shape[0],dtype='float32').dtype)
    #open ground truth
#    output_dict = run_inference_for_single_image(image_np, detection_graph)
    # Visualization of the results of a detection.
    #[ymax,xmin,ymin,xmax]
    vis_util.visualize_boxes_and_labels_on_image_array(
        org_image_np,
        np.array(ground_truth),
        np.ones(ground_truth.shape[0],dtype='int8'),
        np.ones(ground_truth.shape[0],dtype='float32'),
        category_index,
        instance_masks=output_dict.get('detection_masks'),
        use_normalized_coordinates=False,
        line_thickness=8)

#    print("output_dict.get('detection_masks')",output_dict.get('detection_masks'))
    
    #np.append(image_np,org_image_np,axis=1)
    final_img = cv2.cvtColor(np.append(image_np,org_image_np,axis=1),cv2.COLOR_RGB2BGR)
    #cv2.imshow("image",final_img)
    #cv2.waitKey(0)
    ret = cv2.imwrite(os.path.join(PATH_TO_SAVE_IMG_OUT,img_name),final_img)
    #ret = cv2.imwrite(img_name,final_img)
    #print("D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_20000epochs\\test_imgs_output\\"+img_name,os.path.isfile(img_name))
    print(img_name)
    print("done",ret)
#    print(os.getcwd())
#    cv2.imwrite()
#    break
#    plt.figure(figsize=IMAGE_SIZE)
#    plt.imshow(np.append(image_np,org_image_np,axis=1))
    