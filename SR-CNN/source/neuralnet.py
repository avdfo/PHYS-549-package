import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import tensorflow as tf
import numpy as np

class SRNET(object):

    def __init__(self):

        print("\n** Initialize Super-Resolution Network")

        tf.compat.v1.disable_eager_execution()

        self.inputs = tf.compat.v1.placeholder(tf.float32, [None, None, None, None])
        self.outputs = tf.compat.v1.placeholder(tf.float32, [None, None, None, None])

        self.channel = 1
        self.n1 = 64
        self.n2 = 32
        self.f1 = 9
        self.f2 = 1
        self.f3 = 5

        self.weights = {
            'patch_ext': tf.Variable(tf.random.normal([self.f1, self.f1, self.channel, self.n1], stddev=0.001)),
            'nl_map': tf.Variable(tf.random.normal([self.f2, self.f2, self.n1, self.n2], stddev=0.001)),
            'recon': tf.Variable(tf.random.normal([self.f3, self.f3, self.n2, self.channel], stddev=0.001)),
        }
        print("Patch Extraction filter : %s" %(self.weights['patch_ext'].shape))
        print("Non-linear mapping      : %s" %(self.weights['nl_map'].shape))
        print("Reconstruction          : %s" %(self.weights['recon'].shape))

        self.biases = {
            'patch_ext': tf.Variable(tf.zeros([self.n1])),
            'nl_map': tf.Variable(tf.zeros([self.n2])),
            'recon': tf.Variable(tf.zeros([self.channel])),
        }

        self.patch_ext = tf.nn.relu(tf.add(tf.nn.conv2d(self.inputs, self.weights['patch_ext'], strides=[1, 1, 1, 1], padding='SAME'), self.biases['patch_ext']))

        self.nonlinear_map = tf.nn.relu(tf.add(tf.nn.conv2d(self.patch_ext, self.weights['nl_map'], strides=[1, 1, 1, 1], padding='SAME'), self.biases['nl_map']))

        self.recon_temp = tf.add(tf.nn.conv2d(self.nonlinear_map, self.weights['recon'], strides=[1, 1, 1, 1], padding='SAME'), self.biases['recon'])
        self.recon = tf.math.sigmoid(tf.add(tf.nn.conv2d(self.nonlinear_map, self.weights['recon'], strides=[1, 1, 1, 1], padding='SAME'), self.biases['recon']))

        self.loss = tf.reduce_sum(tf.nn.sigmoid_cross_entropy_with_logits(self.outputs, self.recon_temp)) / 90000.
        self.psnr = tf.math.log(1 / tf.sqrt(tf.reduce_mean(tf.square(self.recon - self.outputs)))) / tf.math.log(10.0) * 20

        self.optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=3e-4).minimize(loss=self.loss)

        tf.compat.v1.summary.histogram('w-patch_ext', self.weights['patch_ext'])
        tf.compat.v1.summary.histogram('w-nl_map', self.weights['nl_map'])
        tf.compat.v1.summary.histogram('w-recon', self.weights['recon'])
        tf.compat.v1.summary.histogram('b-patch_ext', self.biases['patch_ext'])
        tf.compat.v1.summary.histogram('b-nl_map', self.biases['nl_map'])
        tf.compat.v1.summary.histogram('b-recon', self.biases['recon'])

        # tf.compat.v1.summary.image('img-inputs', self.inputs)
        # for c_idx in range(self.n1):
        #     tf.compat.v1.summary.image('img-patch_ext %d' %(c_idx), tf.expand_dims(self.patch_ext[:,:,:,c_idx], 3))
        # for c_idx in range(self.n2):
        #     tf.compat.v1.summary.image('img-nonlinear_map %d' %(c_idx), tf.expand_dims(self.nonlinear_map[:,:,:,c_idx], 3))
        # tf.compat.v1.summary.image('img-recon', self.recon)
        # tf.compat.v1.summary.image('img-outputs', self.outputs)

        tf.compat.v1.summary.scalar('loss', self.loss)
        tf.compat.v1.summary.scalar('psnr', self.psnr)

        self.summaries = tf.compat.v1.summary.merge_all()
