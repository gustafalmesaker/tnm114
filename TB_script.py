import tensorflow as tf

for summary in tf.compat.v1.train.summary_iterator('DroneLog/new_training500.0k_1/events.out.tfevents.1733750301.MSI.15336.0'):
    for value in summary.summary.value:
        print(value.tag, value.simple_value)
