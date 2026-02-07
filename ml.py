import pickle
import nltk
import pandas as pd
import string

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier

#gets ntlk list with words like 'an', 'or' 
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def mlpredict(body):
    #open the train model
    with open('models/model.pkl', 'rb') as f:
        #load classifier and vectorizer
        clf, vectorizer = pickle.load(f)
    #convert text into numerical format for training
    X_new = vectorizer.transform([body]).toarray()
    #return prediction (0 for safe, 1 for phishing)
    prediction = clf.predict(X_new)[0]
    return prediction

def mlpreprocess(body):
    
    body = body.replace('\r\n', ' ') # remove linebreak characters

    body = body.lower() # make lowercase

    body = body.translate(str.maketrans('', '', string.punctuation)) # remove punctuation

    stop_words = set(stopwords.words('english')) # define stopwords

    body = ' '.join([w for w in body.split() if w not in stop_words]) #remove stopwords

    return body

def mltrain():

    df = pd.read_csv('data/Phishing_validation_emails.csv') # load raw data
    df = df.rename(columns={'Email Text': 'Body', 'Email Type': 'Label'})  

    df['Label'] = df['Label'].replace({'Safe Email': 0, 'Phishing Email': 1}) # map text labels to numerical values

    df['Body'] = df['Body'].apply(mlpreprocess)

    #convert text into matrixes
    vectorizer = CountVectorizer(max_features=1000)
    X = vectorizer.fit_transform(df['Body']).toarray() # vectorize for machine learning

    y = df['Label'].values

    # save model to models folder
    clf = RandomForestClassifier().fit(X, y)
    with open('models/model.pkl', 'wb') as f:
        pickle.dump((clf, vectorizer), f)


mltrain()

            