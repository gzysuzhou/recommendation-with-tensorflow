import pandas as pd
import numpy as np
import tensorflow as tf

'''
第一步：收集和清洗数据
'''

ratings_df = pd.read_csv('user_score.csv')

#tail命令用于输入文件中的尾部内容。tail命令默认在屏幕上显示指定文件的末尾5行。

posts_df = pd.read_csv('postTag.csv')

posts_df['movieRow'] = posts_df.index

posts_df = posts_df[['movieRow','postID','name']]
#筛选三列出来
posts_df.to_csv('moviesProcessed.csv', index=False, header=True, encoding='utf-8')
#生成一个新的文件moviesProcessed.csv

ratings_df = pd.merge(ratings_df, posts_df, on='postID')
ratings_df.head()

ratings_df = ratings_df[['userID','movieRow','score']]
#筛选出三列
ratings_df.to_csv('ratingsProcessed.csv', index=False, header=True, encoding='utf-8')
#导出一个新的文件ratingsProcessed.csv
ratings_df.head(5)


'''
第二步：创建电影评分矩阵rating和评分纪录矩阵record
'''
userNo = ratings_df['userID'].max() + 1
movieNo = ratings_df['movieRow'].max() + 1
rating = np.zeros((movieNo,userNo))
#创建一个值都是0的数据
flag = 0
ratings_df_length = np.shape(ratings_df)[0]

#查看矩阵ratings_df的第一维度是多少
for index,row in ratings_df.iterrows():
    #interrows（），对表格ratings_df进行遍历
    rating[int(row['movieRow']), int(row['userID'])] = row['score']
    #将ratings_df表里的'movieRow'和'userId'列，填上row的‘评分’
    flag += 1
record = rating > 0
record = np.array(record, dtype = int)
#更改数据类型，0表示用户没有对电影评分，1表示用户已经对电影评分
'''
第三步：构建模型
'''

def normalizeRatings(rating, record):
    m, n =rating.shape
    #m代表电影数量，n代表用户数量
    rating_mean = np.zeros((m,1))
    #每部电影的平均得分
    rating_norm = np.zeros((m,n))
    #处理过的评分
    for i in range(m):
        idx = record[i,:] !=0
        #每部电影的评分，[i，:]表示每一行的所有列
        rating_mean[i] = np.mean(rating[i,idx])
        #第i行，评过份idx的用户的平均得分；
        #np.mean() 对所有元素求均值
        rating_norm[i,idx] -= rating_mean[i]
        #rating_norm = 原始得分-平均得分
    return rating_norm, rating_mean


rating_norm, rating_mean = normalizeRatings(rating, record)
rating_norm =np.nan_to_num(rating_norm)
#对值为NaNN进行处理，改成数值0
rating_mean =np.nan_to_num(rating_mean)
#对值为NaNN进行处理，改成数值0

num_features = 10
X_parameters = tf.Variable(tf.random_normal([movieNo, num_features],stddev = 0.35))
Theta_parameters = tf.Variable(tf.random_normal([userNo, num_features],stddev = 0.35))
#tf.Variables()初始化变量
#tf.random_normal()函数用于从服从指定正太分布的数值中取出指定个数的值，mean: 正态分布的均值。stddev: 正态分布的标准差。dtype: 输出的类型

loss = 1/2 * tf.reduce_sum(((tf.matmul(X_parameters, Theta_parameters, transpose_b = True) - rating_norm) * record) ** 2) + 1/2 * (tf.reduce_sum(X_parameters ** 2) + tf.reduce_sum(Theta_parameters ** 2))
#基于内容的推荐算法模型

optimizer = tf.train.AdamOptimizer(1e-4)
# https://blog.csdn.net/lenbow/article/details/52218551
train = optimizer.minimize(loss)
# Optimizer.minimize对一个损失变量基本上做两件事
# 它计算相对于模型参数的损失梯度。
# 然后应用计算出的梯度来更新变量。

'''
第四步：训练模型
'''
# tf.summary的用法 https://www.cnblogs.com/lyc-seu/p/8647792.html
tf.summary.scalar('loss',loss)
#用来显示标量信息

summaryMerged = tf.summary.merge_all()
#merge_all 可以将所有summary全部保存到磁盘，以便tensorboard显示。
filename = './post_tensorboard'
writer = tf.summary.FileWriter(filename)
#指定一个文件用来保存图。
sess = tf.Session()
#https://www.cnblogs.com/wuzhitj/p/6648610.html
init = tf.global_variables_initializer()
sess.run(init)
#运行

for i in range(10):
     _, movie_summary = sess.run([train, summaryMerged])
     # 把训练的结果summaryMerged存在movie里
     writer.add_summary(movie_summary, i)
     # 把训练的结果保存下来


Current_X_parameters, Current_Theta_parameters = sess.run([X_parameters, Theta_parameters])
# Current_X_parameters为用户内容矩阵，Current_Theta_parameters用户喜好矩阵
predicts = np.dot(Current_X_parameters,Current_Theta_parameters.T) + rating_mean
# dot函数是np中的矩阵乘法，np.dot(x,y) 等价于 x.dot(y)
errors = np.sqrt(np.sum((predicts - rating)**2))
# sqrt(arr) ,计算各元素的平方根


user_id = input('您要想哪位用户进行推荐？请输入用户编号：')
sortedResult = predicts[:, int(user_id)].argsort()[::-1]
# argsort()函数返回的是数组值从小到大的索引值; argsort()[::-1] 返回的是数组值从大到小的索引值
idx = 0
print('为该用户推荐的评分最高的20部作品是：'.center(80,'='))
# center() 返回一个原字符串居中,并使用空格填充至长度 width 的新字符串。默认填充字符为空格。
for i in sortedResult:
    print('评分: %.2f, 作品名: %s' % (predicts[i,int(user_id)],posts_df.iloc[i]['name']))
    # .iloc的用法：https://www.cnblogs.com/harvey888/p/6006200.html
    idx += 1
    if idx == 20:break












