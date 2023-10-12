import numpy as np
import nltk
import random
import string
import sklearn
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nltk.download('punkt')
import pandas
faq = pandas.read_csv("Service.txt", delimiter="\t", header=None, names=["Q", "A"], encoding='iso-8859-1')
faq.shape
qns = faq["Q"]
answers = faq["A"]
TfidfVec = TfidfVectorizer()
tfidf = TfidfVec.fit_transform(qns)
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
def response(user_response):
    robo_response = ''
    Q = ''
    A = ''
    new = TfidfVec.transform([user_response]) #vectorize the input to the same dimension space
    vals = cosine_similarity(new[0], tfidf)
    flat = vals.flatten()
    idx = flat.argsort()[-1]
    sim_max = flat[idx]
    if(sim_max<=0.2):
        robo_response = "I am sorry! I don't have answer for that."
        return robo_response, Q, sim_max, A
       
    else:
        robo_response = "Similar question found!"
        Q = qns[idx]
        A = "Ans: "+answers[idx]
        return robo_response, Q, sim_max, A
        
def say(robo_response, Q, score, A):

  print(A)

flag=True
print("Bill: My name is Bill. I am the Service bot for this recommendation system, if you have any questions, please feel free to ask. If you want to end the conversation, type Bye!")
while(flag==True):
    user_response = input()
    user_response=user_response.lower()
    if(user_response.lower() !='bye'):
        if(user_response=='thanks' or user_response=='thank you' ):
            flag=False
            print("Bill: You are welcome..")
        else:
            if(greeting(user_response)!=None):
                print("Bill: "+greeting(user_response))
            else:
                print("Bill: ",end="")
                say(*response(user_response))
    else:
        flag=False
        print("Bill: Bye! take care...")



