import pandas as pd
import datetime as dt
import os
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
import tidytext
import matplotlib.pyplot as plt
import seaborn as sns

# set working directory
os.chdir(os.path.expanduser("~/Dropbox/Data/Projects/messages"))

# read in the scraped posts
four_locos = pd.read_csv("Data/four_locos.csv")

# instantiate the SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()

# ensure text field is a string
four_locos['text'] = four_locos.text.astype(str)

# run the analyzer on the messages while removing stopwords
scores = []
for txt in four_locos.text:
    tokens = word_tokenize(txt)
    tokens_clean = [word for word in tokens if not word in stopwords.words('english')]
    tokens_sentence = (" ").join(tokens_clean)
    score = vader.polarity_scores(tokens_sentence)
    scores.append(score)

# pull out the compound scores
compound_scores = []
for score in range(0, len(scores)):
    compound_scores.append(scores[score]["compound"])

# histogram of scores
plt.figure(figsize=(9, 5))
sns.distplot(compound_scores).set_title("Distribution of sentiment scores for each text message")
plt.show()

# add the scores to the dataframe
four_locos['sentiment'] = compound_scores

# save to csv
four_locos.to_csv("Data/four_locos.csv", index=False)
