# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
import tensorflow as tf
import time
import redis
import pickle
class Recommand(object):
    
    redis = None
    postKey = "postMap"
    recommandResultKey = "recommandResult"

    def __init__(self):
        Recommand.redis = redis.Redis(host='127.0.0.1', port=6379, db=0)

    def run(self, userID, skip, limit):
        self.cleanData()
        self.createMat()
        self.getTrainModel()
        return self.trainningModel(userID, skip, limit)

    '''
    第一步：收集和清洗数据
    '''
    def cleanData(self):
        ratings_df = pd.read_csv('user_score.csv')
        posts_df = pd.read_csv('postTag.csv')
        posts_df['postRow'] = posts_df.index
        self.posts_df = posts_df[['postRow','postID','name']]
        serliaze = pickle.dumps(self.posts_df)
        Recommand.redis.set(Recommand.postKey, serliaze)
        ratings_df = pd.merge(ratings_df, posts_df, on='postID')
        self.ratings_df = ratings_df[['userID','postRow','score']]
    
    def getPostsDf(self):
        ratings_df = pd.read_csv('user_score.csv')
        posts_df = pd.read_csv('postTag.csv')
        posts_df['postRow'] = posts_df.index
        self.posts_df = posts_df[['postRow','postID','name']]
        serliaze = pickle.dumps(self.posts_df)
        Recommand.redis.set(Recommand.postKey, serliaze)
        return self.postKey

    '''
    第二步：创建作品评分矩阵rating和评分纪录矩阵record
    '''
    def createMat(self):
        self.userNo = self.ratings_df['userID'].max() + 1
        self.postNo = self.ratings_df['postRow'].max() + 1
        rating = np.zeros((self.postNo, self.userNo))
        #创建一个值都是0的数据
        flag = 0
        ratings_df_length = np.shape(self.ratings_df)[0]
        #查看矩阵ratings_df的第一维度是多少
        for index, row in self.ratings_df.iterrows():
            #interrows（），对表格ratings_df进行遍历
            rating[int(row['postRow']), int(row['userID'])] = row['score']
            #将ratings_df表里的'postRow'和'userId'列，填上row的‘评分’
            flag += 1
        record = rating > 0
        self.rating = rating
        #print(self.rating)
        self.record = np.array(record, dtype = int)
        #更改数据类型，0表示用户没有对电影评分，1表示用户已经对电影评分
    '''
    第三步：构建模型
    '''
    def normalizeRatings(self):
        m, n = self.rating.shape
        #m代表电影数量，n代表用户数量
        rating_mean = np.zeros((m,1))
        #每部电影的平均得分
        rating_norm = np.zeros((m,n))
        #处理过的评分
        for i in range(m):
            idx = self.record[i,:] != 0
            #每部电影的评分，[i，:]表示每一行的所有列
            rating_mean[i] = np.mean(self.rating[i,idx])
            #第i行，评过份idx的用户的平均得分；
            #np.mean() 对所有元素求均值
            rating_norm[i,idx] -= rating_mean[i]
            #rating_norm = 原始得分-平均得分
        return rating_norm, rating_mean

    def getTrainModel(self):
        rating_norm, rating_mean = self.normalizeRatings()
        rating_norm = np.nan_to_num(rating_norm)
        #对值为NaNN进行处理，改成数值0
        self.rating_mean = np.nan_to_num(rating_mean)
        #对值为NaNN进行处理，改成数值0

        num_features = 10
        self.X_parameters = tf.Variable(tf.random_normal([self.postNo, num_features],stddev = 0.35))
        self.Theta_parameters = tf.Variable(tf.random_normal([self.userNo, num_features],stddev = 0.35))
        #tf.Variables()初始化变量
        #tf.random_normal()函数用于从服从指定正太分布的数值中取出指定个数的值，mean: 正态分布的均值。stddev: 正态分布的标准差。dtype: 输出的类型

        self.loss = 1/2 * tf.reduce_sum(((tf.matmul(self.X_parameters, self.Theta_parameters, transpose_b = True) - rating_norm) * self.record) ** 2) + 1/2 * (tf.reduce_sum(self.X_parameters ** 2) + tf.reduce_sum(self.Theta_parameters ** 2))
        #基于内容的推荐算法模型

        self.optimizer = tf.train.AdamOptimizer(1e-4)
        # https://blog.csdn.net/lenbow/article/details/52218551
        self.train = self.optimizer.minimize(self.loss)
        # Optimizer.minimize对一个损失变量基本上做两件事
        # 它计算相对于模型参数的损失梯度。
        # 然后应用计算出的梯度来更新变量。

    '''
    第四步：训练模型
    '''
    def trainningModel(self, userID, skip, limit):
        # tf.summary的用法 https://www.cnblogs.com/lyc-seu/p/8647792.html
        tf.summary.scalar('loss',self.loss)
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
        for i in range(1):
            _, post_summary = sess.run([self.train, summaryMerged])
            # 把训练的结果summaryMerged存在post里
            writer.add_summary(post_summary, i)
            # 把训练的结果保存下来
        Current_X_parameters, Current_Theta_parameters = sess.run([self.X_parameters, self.Theta_parameters])
        # Current_X_parameters为用户内容矩阵，Current_Theta_parameters用户喜好矩阵
        predicts = np.dot(Current_X_parameters,Current_Theta_parameters.T) + self.rating_mean
        # 保存到缓存
        serliaze = pickle.dumps(predicts)
        Recommand.redis.set(Recommand.recommandResultKey, serliaze)
        # dot函数是np中的矩阵乘法，np.dot(x,y) 等价于 x.dot(y)
        errors = np.sqrt(np.sum((predicts - self.rating)**2))
        # sqrt(arr) ,计算各元素的平方根
        sortedResult = predicts[:, int(userID)].argsort()[::-1]
        # argsort()函数返回的是数组值从小到大的索引值; argsort()[::-1] 返回的是数组值从大到小的索引值
        idx = num_skip = 0
        hasNextPage = True
        nextCursor = 0
        totalCount = len(predicts)
        if skip + limit >= totalCount:
            hasNextPage = False
        if hasNextPage:
            nextCursor = skip + limit
        recommandations = []
        for i in sortedResult:
            #print('评分: %.2f, 作品ID: %s' % (predicts[i,int(userID)],self.posts_df.iloc[i]['postID']))
            if (skip > 0):
                if (num_skip > skip-1):
                    recommandations.append({"postID": self.posts_df.iloc[i]['postID'], "score": predicts[i,int(userID)]})
                    idx += 1
                    if idx == limit:break
                else:
                    num_skip += 1
                    continue
            else:
                recommandations.append({"postID": self.posts_df.iloc[i]['postID'], "score": predicts[i,int(userID)]})
                idx += 1
                if idx == limit:break
        return recommandations, totalCount, hasNextPage, nextCursor

    
    def getRecommand(self, userID, skip = 0, limit = 30):
        cacheRecommand = Recommand.redis.get(Recommand.recommandResultKey)
        cachePostMap = Recommand.redis.get(Recommand.postKey)
        posts_df = []
        recommandations = []
        if cacheRecommand:
            predicts = pickle.loads(cacheRecommand)
            sortedResult = predicts[:, int(userID)].argsort()[::-1]
            # argsort()函数返回的是数组值从小到大的索引值; argsort()[::-1] 返回的是数组值从大到小的索引值
            idx = num_skip = 0
            hasNextPage = True
            nextCursor = 0
            totalCount = len(predicts)
            if skip + limit >= totalCount:
                hasNextPage = False
            if hasNextPage:
                nextCursor = skip + limit
            if cachePostMap:
                posts_df = pickle.loads(cachePostMap)
            else:
                posts_df = self.getPostsDf()
            for i in sortedResult:
                if (skip > 0):
                    if (num_skip > skip-1):
                        recommandations.append({"postID": posts_df.iloc[i]['postID'], "score": predicts[i,int(userID)]})
                        idx += 1
                        if idx == limit:break
                    else:
                        num_skip += 1
                        continue
                else:
                    recommandations.append({"postID": posts_df.iloc[i]['postID'], "score": predicts[i,int(userID)]})
                    idx += 1
                    if idx == limit:break
            return recommandations, totalCount, hasNextPage, nextCursor
        else:
            return self.run(userID, skip, limit)
            
