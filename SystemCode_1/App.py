from flask import Flask, render_template, request
import pickle
import numpy as np
import nltk
import random
import string
import sklearn
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import pandas as pd

nltk.download('punkt')

app = Flask(__name__)

# Load FAQ data
faq = pd.read_csv("Service.txt", delimiter="\t", header=None, names=["Q", "A"], encoding='iso-8859-1')
qns = faq["Q"]
answers = faq["A"]
TfidfVec = TfidfVectorizer()
tfidf = TfidfVec.fit_transform(qns)

# Load game recommendation data
new_df = pickle.load(open("C:/Users/19928/Desktop/Projects/Project-1/Code/game_data.pkl", 'rb'))
vectors = pickle.load(open("C:/Users/19928/Desktop/Projects/Project-1/Code/vectors.pkl", 'rb'))
cv = pickle.load(open("C:/Users/19928/Desktop/Projects/Project-1/Code/cv.pkl", 'rb'))
similarity = pickle.load(open("C:/Users/19928/Desktop/Projects/Project-1/Code/similarity.pkl", 'rb'))

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey")
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

def response(user_response):
    robo_response = ''
    Q = ''
    A = ''
    new = TfidfVec.transform([user_response])  # vectorize the input to the same dimension space
    vals = cosine_similarity(new[0], tfidf)
    flat = vals.flatten()
    idx = flat.argsort()[-1]
    sim_max = flat[idx]
    if sim_max <= 0.2:
        robo_response = "I am sorry! I don't have an answer for that."
        return robo_response, Q, sim_max, A
    else:
        robo_response = "Similar question found!"
        Q = qns[idx]
        A = "Bill: " + answers[idx]
        return robo_response, Q, sim_max, A

def say(robo_response, Q, score, A):
    print(A)
    return A

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.form['user_input']
    user_input = user_input.lower()
    if user_input == 'bye':
        Answer="Bill: Bye! Take care..."
        return render_template('Chatbot.html', Answers=Answer)
    else:
        if user_input == 'thanks' or user_input == 'thank you':
            Answer="Bill: You are welcome.."
            return render_template('Chatbot.html', Answers=Answer)
        else:
            Answer=say(*response(user_input))
            return render_template('Chatbot.html', Answers=Answer)



@app.route('/recommend', methods=['POST'])
def recommend():
    game_name = request.form['game_name']
    index = new_df[new_df['Name'] == game_name].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_games = [(new_df.iloc[i[0]]['Name'], new_df.iloc[i[0]]['About the game']) for i in distances[1:6]]
    return render_template('recommend.html', game_name=game_name, recommended_games=recommended_games)

@app.route('/recommend_genre', methods=['POST'])
def recommend_genre():
    genre = request.form['genre']
    genre_vector = cv.transform([genre]).toarray()
    distances = []
    for i in range(len(vectors)):
        a = vectors[i, :]
        a = a.reshape(1, -1)
        distance = euclidean_distances(genre_vector, a)
        distances.append((distance, i))
    distances = sorted(distances, key=lambda x: x[0])
    min_distances = distances[:5]
    min_indexes = [idx for _, idx in min_distances]
    recommended_games = [(new_df.iloc[idx]['Name'],new_df.iloc[idx]['About the game']) for idx in min_indexes]
    return render_template('recommend_genre.html', genre=genre, recommended_games=recommended_games)

if __name__ == '__main__':
    app.run(debug=True)