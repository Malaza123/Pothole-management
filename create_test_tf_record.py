import os
import io
import pandas as pd
import tensorflow as tf
from PIL import Image

def create_tf_example(row, image_dir):
    filename = row['filename']
    img_path = os.path.join(image_dir, filename)
    
    with tf.io.gfile.GFile(img_path, 'rb') as fid:
        encoded_jpg = fid.read()

    image = Image.open(io.BytesIO(encoded_jpg))
    width, height = image.size

    xmins = [row['xmin'] / width]
    xmaxs = [row['xmax'] / width]
    ymins = [row['ymin'] / height]
    ymaxs = [row['ymax'] / height]

    classes_text = [row['class'].encode('utf8')]
    classes = [1]  # Assuming one class for simplicity

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': tf.train.Feature(int64_list=tf.train.Int64List(value=[height])),
        'image/width': tf.train.Feature(int64_list=tf.train.Int64List(value=[width])),
        'image/filename': tf.train.Feature(bytes_list=tf.train.BytesList(value=[filename.encode('utf8')])),
        'image/source_id': tf.train.Feature(bytes_list=tf.train.BytesList(value=[filename.encode('utf8')])),
        'image/key/sha256': tf.train.Feature(bytes_list=tf.train.BytesList(value=[filename.encode('utf8')])),
        'image/encoded': tf.train.Feature(bytes_list=tf.train.BytesList(value=[encoded_jpg])),
        'image/format': tf.train.Feature(bytes_list=tf.train.BytesList(value=['jpeg'.encode('utf8')])),
        'image/object/bbox/xmin': tf.train.Feature(float_list=tf.train.FloatList(value=xmins)),
        'image/object/bbox/xmax': tf.train.Feature(float_list=tf.train.FloatList(value=xmaxs)),
        'image/object/bbox/ymin': tf.train.Feature(float_list=tf.train.FloatList(value=ymins)),
        'image/object/bbox/ymax': tf.train.Feature(float_list=tf.train.FloatList(value=ymaxs)),
        'image/object/class/text': tf.train.Feature(bytes_list=tf.train.BytesList(value=classes_text)),
        'image/object/class/label': tf.train.Feature(int64_list=tf.train.Int64List(value=classes)),
    }))

    return tf_example

def main():
    csv_path = 'path/to/train_labels.csv'
    image_dir = 'path/to/train/images'
    output_path = 'path/to/output/train.record'

    df = pd.read_csv(csv_path)
    
    with tf.io.TFRecordWriter(output_path) as writer:
        for _, row in df.iterrows():
            tf_example = create_tf_example(row, image_dir)
            writer.write(tf_example.SerializeToString())

if __name__ == '__main__':
    main()
