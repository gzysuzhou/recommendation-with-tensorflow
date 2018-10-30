import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
 
num_points = 1000
vectors_set = []
for i in range(num_points):
  x1 = np.random.normal(0.0, 0.55)
  y1 = x1*0.1 + 0.3 + np.random.normal(0.0, 0.03)
  vectors_set.append([x1, y1])
 
x_data = [v[0] for v in vectors_set]
y_data = [v[1] for v in vectors_set]
 
plt.scatter(x_data, y_data, c='r')
#plt.show()

#生成一维的w矩阵，取值为[-1，1]之间的随机数
w = tf.Variable(tf.random_uniform([1],-1.0,1.0),name='W')
#生成一维的b矩阵，初始值为0
b = tf.Variable(tf.zeros([1]),name='b')
y = w*x_data+b
 
#均方误差
loss = tf.reduce_mean(tf.square(y-y_data),name='loss')
#梯度下降
optimizer = tf.train.GradientDescentOptimizer(0.5)
#最小化loss
train = optimizer.minimize(loss,name='train')
 
 
sess=tf.Session()
init = tf.global_variables_initializer()
sess.run(init)
 
#print("W",sess.run(w),"b=",sess.run(b),"loss=",sess.run(loss))
for step in range(20):
  sess.run(train)
  print("W=",sess.run(w),"b=",sess.run(b),"loss=",sess.run(loss))
 
plt.scatter(x_data,y_data,c='r')
plt.plot(x_data,sess.run(w)*x_data+sess.run(b))
plt.title("y=wx+b")
plt.show()
