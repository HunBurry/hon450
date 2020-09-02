from sklearn.feature_extraction.text import CountVectorizer
import re
import pandas as pd 
import numpy as np 
import seaborn as sns
import string
import nltk
import warnings 
warnings.filterwarnings("ignore", category=DeprecationWarning)
from nltk import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
import gensim;
import spacy;

def pos_tagging(data):
    req_tag = ['NN']
    extracted_words = []
    i = 0;
    try:
        for x in data['parsed_tweet']:
            doc = spacy(x)
            for token in doc:
                i += 1
                if token.tag_ in req_tag and token.shape_ != 'x' and token.shape_ != 'xx' and token.shape_ != 'xxx':
                    extracted_words.append(token.lemma_)
        return extracted_words
    except Exception as e:
        return extracted_words

'''
def word2vec(data):
    terms = listoflist(data)
    try:
        filtered_terms = []
        for i in range(len(terms)):
            corrent_words = [token for token in terms[i] if token in model_wiki.wv.vocab]
            if len(corrent_words) > 0 :
                filtered_terms.append(corrent_words[0])
        vector_of_terms = []
        for x in range(len(filtered_terms)):
            vector_of_terms.append(model_wiki.wv[filtered_terms[x]])
        return vector_of_terms,filtered_terms
    except Exception as e:
        return abort(Response(
            json.dumps({'status_code': 400, 'success': False, 'message': 'Something went wrong'}),
            mimetype="application/json"))

def feature_sentiment(sentence, pos, neg):
    #input: dictionary and sentence
    #function: appends dictionary with new features if the feature
    #          did not exist previously,then updates sentiment to
    #          each of the new or existing features
    #output: updated dictionary
    sent_dict = dict()
    sentence = spacy(sentence)
    opinion_words = neg + pos
    debug = 0
    for token in sentence:
        # check if the word is an opinion word, then assign sentiment
        if token.text in opinion_words:
            sentiment = 1 if token.text in pos else -1
            if (token.dep_ == "advmod"):
                continue
            elif (token.dep_ == "amod"):
                sent_dict[token.head.text] = sentiment
            else:
                for child in token.children:
                    # if there's a adj modifier (i.e. very, pretty, etc.) add more weight to sentiment
                    # This could be better updated for modifiers that either positively or negatively emphasize
                    if ((child.dep_ == "amod") or (child.dep_ == "advmod")) and (child.text in opinion_words):
                        sentiment *= 1.5
                    # check for negation words and flip the sign of sentiment
                    if child.dep_ == "neg":
                        sentiment *= -1
                for child in token.children:
                    # if verb, check if there's a direct object
                    if (token.pos_ == "VERB") & (child.dep_ == "dobj"):                        
                        sent_dict[child.text] = sentiment
                        # check for conjugates (a AND b), then add both to dictionary
                        subchildren = []
                        conj = 0
                        for subchild in child.children:
                            if subchild.text == "and":
                                conj=1
                            if (conj == 1) and (subchild.text != "and"):
                                subchildren.append(subchild.text)
                                conj = 0
                        for subchild in subchildren:
                            sent_dict[subchild] = sentiment

                # check for negation
                for child in token.head.children:
                    noun = ""
                    if ((child.dep_ == "amod") or (child.dep_ == "advmod")) and (child.text in opinion_words):
                        sentiment *= 1.5
                    # check for negation words and flip the sign of sentiment
                    if (child.dep_ == "neg"): 
                        sentiment *= -1
                
                # check for nouns
                for child in token.head.children:
                    noun = ""
                    if (child.pos_ == "NOUN") and (child.text not in sent_dict):
                        noun = child.text
                        # Check for compound nouns
                        for subchild in child.children:
                            if subchild.dep_ == "compound":
                                noun = subchild.text + " " + noun
                        sent_dict[noun] = sentiment
                    debug += 1
    return sent_dict
'''

def main(): 
    train = pd.read_csv('../data/data12_04_2020_22-58.csv')

    train_original = train.copy()

    test = pd.read_csv('../data/data12_02_2020_11-32.csv')

    test_original = test.copy()

    train = train.drop(train.columns[[1, 3, 4, 6]], axis=1)
    test = test.drop(test.columns[[1, 3, 4, 6]], axis=1)
    test = test.dropna();
    train = train.dropna();

    train.columns = ['id', 'tweet', 'party']
    test.columns = ['id', 'tweet', 'party']

################################################################################################################################

    combine = train.append(test, ignore_index=True, sort=True)

    combine['parsed_tweet'] = combine['tweet'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>2]))

    tokenized_tweet = combine['parsed_tweet'].apply(lambda x: x.split())
    ps = PorterStemmer()
    tokenized_tweet = tokenized_tweet.apply(lambda x: [ps.stem(i) for i in x])

    for i in range(len(tokenized_tweet)):
        tokenized_tweet[i] = ' '.join(tokenized_tweet[i])

    combine['parsed_tweet'] = tokenized_tweet;

    all_words_repub = ' '.join(text for text in combine['parsed_tweet'][combine['party'] == 'R'])
    all_words_demo = ' '.join(text for text in combine['parsed_tweet'][combine['party'] == 'D'])

    extract_words = pos_tagging(data)

    ###############################################################################################################################

    bow_vectorizer = CountVectorizer(max_df=0.90, min_df=2, stop_words='english')
    bagOfWords = bow_vectorizer.fit_transform(combine['parsed_tweet'])

    tfidf = TfidfVectorizer(max_df=0.90, min_df=2, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(combine['parsed_tweet'])

    x_train_bow = bagOfWords.todense();
    y_train_bow = combine['party']

    x_train_tfidf = tfidf_matrix.todense();
    y_train_tfidf = combine['party']

    ################################################################################################################################

    recentTrumpTweet = []
    initialTweet = "We had FAR more people (many millions) watching us at the RNC than did Sleepy Joe and the DNC, and yet an ad just ran saying the opposite. This is what we’re up against. Lies. But we will WIN!"
    parsed = ' '.join([w for w in initialTweet.split() if len(w)>2]))
    parsed = parsed.split();
    recentTrumpTweet = [ps.stem(i) for i in parsed]
    recentTrumpTweet = ' '.join([word for word in recentTrumpTweet])

    log_reg = LogisticRegression(random_state=5,solver='lbfgs')
    log_reg.fit(x_train_bow, y_train_bow)

    prediction_bow = log_reg.predict_proba(recentTrumpTweet)
    #prediction_int = prediction_bow[:,1]>=0.3
    #prediction_int = prediction_int.astype(np.int)
    #log_bow = f1_score(y_valid_bow, prediction_int)

    log_reg.fit(x_train_tfidf, y_train_tfidf)
    prediction_tfidf = log_reg.predict_proba(recentTrumpTweet)
    #prediction_int = prediction_tfidf[:,1]>=0.3
    #prediction_int = prediction_int.astype(np.int)
    #log_tfidf = f1_score(y_valid_tfidf, prediction_int)

    ###############################################################################################################################

    model_bow = XGBClassifier(random_state=9,learning_rate=0.9)
    model_bow.fit(x_train_bow, y_train_bow)
    xgb = model_bow.predict_proba(recentTrumpTweet)

    #xgb=xgb[:,1]>=0.3
    #xgb_int=xgb.astype(np.int)
    #xgb_bow=f1_score(y_valid_bow,xgb_int)

    model_tfidf = XGBClassifier(random_state=38,learning_rate=0.9)
    model_tfidf.fit(x_train_tfidf, y_train_tfidf)
    tfidfres = model_tfidf.predict_proba(recentTrumpTweet)
    #xgb_tfidf=xgb_tfidf[:,1]>=0.3
    #xgb_int_tfidf=xgb_tfidf.astype(np.int)
    #score=f1_score(y_valid_tfidf,xgb_int_tfidf)

    ###############################################################################################################################

if __name__ == '__main__':
    main();