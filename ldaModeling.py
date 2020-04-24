# -*- coding: utf-8 -*-
import sys
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import emoji

import gensim

import csv
import re

#http://www.tweepy.org/
import tweepy
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk import ngrams
from nltk.stem.api import StemmerI
from nltk.stem.regexp import RegexpStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.isri import ISRIStemmer
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.stem.rslp import RSLPStemmer
from stemming.porter2 import stem

import emoji

consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

def search_tweets():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)


    searchQuery = '@emirates'  # this is what we're searching for
    maxTweets = 10000 # Some arbitrary large number
    tweetsPerQry = 100  # this is the max the API permits
    fName = 'emirates_mentioned_tweets' # We'll store the tweets in a text file.
    lang = 'en'

    sinceId = None
    max_id = -1L

    tokenizer = RegexpTokenizer(r'\w+')
    en_stop_words = set(stopwords.words('english'))
    stemmer = SnowballStemmer("english")
    p_stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()

    tweetCount = 0
    tweetsSet = []

    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, tweet_mode='extended', lang = lang, count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery, tweet_mode='extended', lang = lang, count=tweetsPerQry,
                                            since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, tweet_mode='extended', lang = lang, count=tweetsPerQry,
                                            max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, tweet_mode='extended', lang = lang, count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break

            for tweet in new_tweets:
                raw = tweet.full_text.encode("utf-8").lower()

                # print ("before raw: " + raw)
                # raw = re.sub(r'^https?:\/\/.*[\r\n]*', '', raw, flags=re.MULTILINE)
                raw = re.sub(r"http\S+", "", raw)
                raw = re.sub(r'[^\w]', ' ', raw)
                # print ("after raw: " + raw)
                tokens = tokenizer.tokenize(raw)
                stopped_tokens = [i for i in tokens if not i in en_stop_words]
                emoji_tokens = [i for i in stopped_tokens if not i in emoji.UNICODE_EMOJI]


                # lema_tokens = [p_stemmer.stem(i) for i in emoji_tokens]
                lema_tokens = []
                for i in emoji_tokens:
                    try:
                        # w = stemmer.stem(r)
                        w = lemmatizer.lemmatize(i.decode('utf-8'))
                    except UnicodeDecodeError:
                        try:
                            w = lemmatizer.lemmatize(i)
                            # w = r.encode('utf-8')
                            # w = stemmer.stem(r.decode('utf-8'))
                            print ("ERROR: UnicodeDecodeError " + raw)
                        except UnicodeEncodeError:
                            w = i
                            print ("ERROR: UnicodeEncodeError " + raw)

                    lema_tokens.append(w)



                tweetsSet.append(lema_tokens)
            # turn our tokenized documents into a id <-> term dictionary

            tweetCount += len(new_tweets)
            print("Downloaded {0} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break
    print ("tweetsset size {0}".format(len(tweetsSet)))

    dictionary = corpora.Dictionary(tweetsSet)

    # convert tokenized documents into a document-term matrix
    corpus = [dictionary.doc2bow(text) for text in tweetsSet]

    # generate LDA model
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=25, id2word = dictionary, passes=20)

    print(ldamodel.print_topics(num_topics=25, num_words=5))


#if we're running this as a script
if __name__ == '__main__':
    #get tweets for query word passed at command line
    search_tweets()
