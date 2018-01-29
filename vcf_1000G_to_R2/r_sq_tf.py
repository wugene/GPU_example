# coding: utf-8

import tensorflow as tf

# n * m matrix X
# 1 * m matrix y
def r_square(X, y):

    x_tf = tf.placeholder('float32', (None,None))
    y_tf = tf.placeholder('float32', (1, None))

    x_bar = tf.reduce_mean(x_tf, axis=1, keep_dims=True)
    y_bar = tf.reduce_mean(y_tf)

    x_2 = x_tf - x_bar
    y_2 = y_tf - y_bar

    x_SS = tf.reduce_sum((x_2 * x_2), axis=1, keep_dims=True)
    y_SS = tf.reduce_sum( y_2 * y_2)

    xy_sum = tf.matmul(x_2, y_2, transpose_b=True)

    r2_tf = xy_sum * xy_sum / (x_SS * y_SS)

    with tf.Session() as sess:
        r2 = sess.run(r2_tf, feed_dict={x_tf: X, y_tf: y})

    return r2


