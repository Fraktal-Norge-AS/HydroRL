import tensorflow as tf
from pathlib import Path
from server.appsettings import appSettings
import os


def per_process_gpu_init():
    if not appSettings.use_gpu():
        tf.config.set_visible_devices([], "GPU")
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  # see issue #152
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
