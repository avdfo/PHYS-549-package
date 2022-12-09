import os, argparse
os.environ["CUDA_VISIBLE_DEVICES"]="0"

import tensorflow as tf

import source.neuralnet as nn
import source.datamanager as dman
import source.tf_process as tfp
#import source.stamper as stamper
#stamper.print_stamp()

def main():

    srnet = nn.SRNET()

    dataset = dman.DataSet()

    sess = tf.compat.v1.InteractiveSession()
    sess.run(tf.compat.v1.global_variables_initializer())
    saver = tf.compat.v1.train.Saver()

    tfp.training(sess=sess, neuralnet=srnet, saver=saver, dataset=dataset, epochs=FLAGS.epoch, batch_size=FLAGS.batch, batch_size_val=FLAGS.batch_val)
    tfp.testing(sess=sess, neuralnet=srnet, saver=saver, dataset=dataset)
    tfp.testing_exp(sess=sess, neuralnet=srnet, saver=saver, dataset=dataset)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--epoch', type=int, default=200, help='-')
    parser.add_argument('--batch', type=int, default=16, help='-')
    parser.add_argument('--batch_val', type=int, default=4, help='-')

    FLAGS, unparsed = parser.parse_known_args()

    main()
