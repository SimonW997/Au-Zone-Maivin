import atexit  
import sys  
import zenoh  
import time 
from argparse import ArgumentParser  
from PIL import Image 
import os  
import ctypes  
import numpy as np 

import deepview.vaal as vaal  # Importing vaal module from deepview package
from deepview.rt.tensor import Tensor  # Importing Tensor class from deepview package
from edgefirst.schemas.edgefirst_msgs.DmaBuffer import DmaBuffer as buf  # Importing DmaBuffer class from edgefirst package for message serialization

SYS_pidfd_getfd = 438  # Assigning the syscall number for pidfd_open to a constant variable
libc = ctypes.CDLL(None, use_errno=True)  # Loading the C standard library
ctx = vaal.Context("cpu")  # Creating a vaal context object for CPU
tensor = Tensor(shape=[1080,1920,3], dtype=np.uint8)  # Creating a Tensor object with specified shape and data type

def get_jpeg_from_fd(dma):
    # Defining a function to retrieve JPEG image from file descriptor
    pidfd = os.pidfd_open(dma.pid)  # Opening a file descriptor for the process ID
    ret = libc.syscall(SYS_pidfd_getfd, pidfd, dma.fd, 0)  # Invoking the syscall to get the file descriptor
    ctx.load_frame(dma.width, dma.height, dma.fourcc, ret, tensor)  # Loading frame data into the Tensor object
    numpy_array = np.clip(tensor.array(), 0, 255).astype(np.uint8)  # Clipping and converting Tensor array to numpy array
    mcap_image = Image.fromarray(numpy_array)  # Creating an image object from the numpy array
    mcap_image.save("output.jpg", format="JPEG", quality=100)  # Saving the image as JPEG format to output.jpg

def parse_args():
    # Defining a function to parse command-line arguments
    parser = ArgumentParser(description="Topics Example")  # Creating an ArgumentParser object with description
    parser.add_argument('-c', '--connect', type=str, default='tcp/127.0.0.1:7447',
                        help="Connection point for the zenoh session, default='tcp/127.0.0.1:7447'")
                        # Adding argument for specifying connection point
    parser.add_argument('-t', '--time', type=float, default=5,
                        help="Time to run the subscriber before exiting.")
                        # Adding argument for specifying running time of the subscriber
    parser.add_argument('topic', nargs='?', default="rt/camera/dma", type=str, help='The topic to which to subscribe. Default: rt/camera/dma')
    return parser.parse_args()  # Parsing and returning the parsed arguments

def message_callback(msg):
    # Defining a function to handle received messages
    global received_message  # Declaring a global variable to store received message
    received_message = bytes(msg.value.payload)  # Extracting payload from the message and storing it
    dma = buf.deserialize(received_message)  # Deserializing the received message into DmaBuffer object
    get_jpeg_from_fd(dma)  # Calling a function to retrieve JPEG image from DmaBuffer

def main():
    # Defining the main function
    args = parse_args()  # Parsing command-line arguments
    cfg = zenoh.Config()  # Creating a zenoh Config object
    cfg.insert_json5(zenoh.config.CONNECT_KEY, '["%s"]' % args.connect)  # Inserting connection key into the config
    session = zenoh.open(cfg)  # Opening a zenoh session with the specified config
    def _on_exit():
        # Defining a function to be executed on exit
        session.close()  # Closing the zenoh session
    atexit.register(_on_exit)  # Registering the exit function to be executed at program termination

    sub = session.declare_subscriber(args.topic, message_callback)  # Declaring a subscriber for the specified topic
    time.sleep(args.time)  # Sleeping for the specified time period