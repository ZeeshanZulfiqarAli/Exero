import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
#from matplotlib import pyplot as plt
#from PIL import Image
import glob
import xml.etree.ElementTree as ET
import time

# This is needed since the notebook is stored in the object_detection folder.
#sys.path.append("..")
from .utils import ops as utils_ops
from .utils import label_map_util
from .utils import visualization_utils as vis_util


# This is needed to display the images.
#%matplotlib inline

class detection():

    def __init__(self,w=None,h=None):
        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else: # Not frozen
            directory = os.path.dirname(__file__)
            #directory = r"D:\zeeshan work\fyp gui\Exero\exero"
            directory = directory.split("\\")
            directory = '\\'.join(directory[:-1])
            print(directory)

        self.PATH_TO_CKPT = os.path.join(directory, 'model', '4(2)_frozen_inference_graph.pb')
        self.PATH_TO_LABELS = os.path.join(directory, 'model', 'my_label_map.pbtxt')
            
        ##self.PATH_TO_CKPT = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_14556+25000epochs_dropout90_autoaugment_lr0.004_step2000_rate95\\4(2)_frozen_inference_graph.pb"
        #self.PATH_TO_CKPT = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_25000epochs_adam_dropout90_autoaugment_lr0.004_step2000_decayRate95\\5_frozen_inference_graph.pb"
        ##self.PATH_TO_LABELS = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_20000epochs_rmsProp_lr0.004\\my_label_map.pbtxt"
        #PATH_TO_TEST_VID = "D:\\assignments\\fyp\\WL.mp4"
        #PATH_TO_OUTPUT_VID = "D:\\TensorFlow\\workspace\\fyp_ssd_inception_v2_25000epochs_adam_dropout90_autoaugment_lr0.004_step2000_decayRate95\\"
        #path = "D:\\assignments\\fyp\\Kvasir-SEG\\test_xml\\" #xml path
        self.num_classes = 1
        if w is not None and h is not None:
            self.width = int(w)
            self.height = int(h)
        else:
            self.width = None
            self.height = None
        #os.path.exists()
        

    def load_model(self):
        self._detection_graph = tf.Graph()
        #print("44444")
        #with self._detection_graph.as_default():
        self._graph = self._detection_graph.as_default()
        od_graph_def = tf.GraphDef()

        with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')


        label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=self.num_classes, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        #self._graph = self._detection_graph.as_default()
        self.sess = tf.Session()
        # Get handles to input and output tensors
        ops = tf.get_default_graph().get_operations()
        all_tensor_names = {
            output.name for op in ops for output in op.outputs}
        self._tensor_dict = {}
        for key in [
            'num_detections', 'detection_boxes', 'detection_scores',
            'detection_classes', 'detection_masks'
        ]:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
                self._tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                    tensor_name)
        if 'detection_masks' in self._tensor_dict:
            # The following processing is only for single image
            self.detection_boxes = tf.squeeze(
                self._tensor_dict['detection_boxes'], [0])
            self.detection_masks = tf.squeeze(
                self._tensor_dict['detection_masks'], [0])
            # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
            real_num_detection = tf.cast(
                self._tensor_dict['num_detections'][0], tf.int32)
            self.detection_boxes = tf.slice(self.detection_boxes, [0, 0], [
                                    real_num_detection, -1])
            self.detection_masks = tf.slice(self.detection_masks, [0, 0, 0], [
                                    real_num_detection, -1, -1])
        self.var = "myname"
        if self.width is not None and self.height is not None:
            self.load_model_2()

    def load_model_2(self,flag = True):
        print(self.var)
        #part 2 of load model. use when width and height is known
        if 'detection_masks' in self._tensor_dict:
            detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                self.detection_masks, self.detection_boxes, self.width, self.height)
            print(self.width, self.height)
            detection_masks_reframed = tf.cast(
                tf.greater(detection_masks_reframed, 0.5), tf.uint8)
            # Follow the convention by adding back the batch dimension
            self._tensor_dict['detection_masks'] = tf.expand_dims(
                detection_masks_reframed, 0)
        if flag:
            self._image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

    def setSize(self,w,h):
        self.width = int(w)
        self.height = int(h)
        
    def advanced_run_inference_for_single_image(self,image):

        t1 = time.time()
        # Run inference
        output_dict = self.sess.run(self._tensor_dict,
                            feed_dict={self._image_tensor: np.expand_dims(image, 0)})
        t2 = time.time() - t1
        #print("aa: ",t2)
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

    def run_inference_for_single_image(self,image, graph):
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
                    self.detection_boxes = tf.squeeze(
                        tensor_dict['detection_boxes'], [0])
                    self.detection_masks = tf.squeeze(
                        tensor_dict['detection_masks'], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tf.cast(
                        tensor_dict['num_detections'][0], tf.int32)
                    self.detection_boxes = tf.slice(self.detection_boxes, [0, 0], [
                                            real_num_detection, -1])
                    self.detection_masks = tf.slice(self.detection_masks, [0, 0, 0], [
                                            real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        self.detection_masks, self.detection_boxes, image.shape[0], image.shape[1])
                    detection_masks_reframed = tf.cast(
                        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    # Follow the convention by adding back the batch dimension
                    tensor_dict['detection_masks'] = tf.expand_dims(
                        detection_masks_reframed, 0)
                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
                t1 = time.time()
                # Run inference
                output_dict = sess.run(tensor_dict,
                                    feed_dict={image_tensor: np.expand_dims(image, 0)})
                t2 = time.time() - t1
                #print("aa: ",t2)
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

    def detect(self,frame):
        
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        #image_np_expanded = np.expand_dims(frame, axis=0)
        # Actual detection.
        t1 = time.time()
        #output_dict = self.run_inference_for_single_image(frame, self._detection_graph)
        output_dict = self.advanced_run_inference_for_single_image(frame)
        t2 = time.time() - t1
        print("t22: ",t2)
        # Visualization of the results of a detection.
        t1 = time.time()
        '''vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            self.category_index,
            instance_masks=output_dict.get('detection_masks'),
            use_normalized_coordinates=True,
            line_thickness=8)'''
        l = vis_util.get_bounding_box(
            frame,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            self.category_index,
            min_score_thresh=.5)
        # write the flipped frame
        #print("apple")
        #print("l",l)
        #print("vis time: ",time.time()-t1)
        #print("details:",output_dict['detection_boxes'], output_dict['detection_classes'], output_dict['detection_scores'],self.category_index)
        print("lllllllllllllllllllllllllllllllllllllllllllllllllll",l,type(l))
        return frame,l
    
    def close(self):
        self.sess.close()
        #self._detection_graph.close()
    #  Release everything if job is finished
    #cv2.destroyAllWindows()
        