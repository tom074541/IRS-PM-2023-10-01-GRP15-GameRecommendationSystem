import pandas as pd
import numpy as np
import os
import pickle
games_data=pd.read_csv('C:/Users/19928/Desktop/Projects/Project-1/Code/game.csv')
games_data.head()
games_data=games_data[['AppID','Name','About the game','Categories','Genres','Tags']]
#Natural language processing
new_games_data=pd.DataFrame(games_data)
#字符串按空格进行分割
new_games_data['Genres']=new_games_data['Genres'].apply(lambda x:x.split())
new_games_data['Categories']=new_games_data['Categories'].apply(lambda x:x.split())
new_games_data['Tags']=new_games_data['Tags'].apply(lambda x:x.split())
new_games_data['About the game']=new_games_data['About the game'].apply(lambda x:x.split())
#移除三列中的空格
new_games_data['Categories']=new_games_data['Categories'].apply(lambda x:[i.replace(" ","") for i in x])
new_games_data['Genres']=new_games_data['Genres'].apply(lambda x:[i.replace(" ","") for i in x])
new_games_data['Tags']=new_games_data['Tags'].apply(lambda x:[i.replace(" ","") for i in x])
#形成新列
new_games_data['tags']=new_games_data['About the game'] + new_games_data['Categories'] + new_games_data['Genres'] + new_games_data['Tags']
#形成新Dataframe
new_df=new_games_data[['AppID','Name','tags']]
#小写并通过空格连接
new_df['tags']=new_df['tags'].apply(lambda x:" ".join(x))
new_df['tags']=new_df['tags'].apply(lambda x:x.lower())
#词干提取
from nltk.stem.porter import PorterStemmer
ps= PorterStemmer()
def stem(text):
  y=[]
  for i in text.split():
    y.append(ps.stem(i))
  return " ".join(y)
new_df['tags']=new_df['tags'].apply(stem)
#计数向量,每个单词在每一个tags字段是否出现，是：1，否;0
from sklearn.feature_extraction.text import CountVectorizer
cv=CountVectorizer(max_features=5000,stop_words='english')
vectors=cv.fit_transform(new_df['tags']).toarray()
print(vectors.shape)
#计算相似度矩阵
from sklearn.metrics.pairwise import cosine_similarity
similarity=cosine_similarity(vectors)
def recommend(game):
    index = new_df[new_df['Name'] == game].index[0]
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    for i in distances[1:6]:
        print(new_df.iloc[i[0]].Name)
print(similarity.shape)
first_row = similarity[0]
print(first_row)
save_path = 'C:/Users/19928/Desktop/Projects/Project-1/Code/similarity.pkl'
pickle.dump(similarity, open(save_path, 'wb'))
