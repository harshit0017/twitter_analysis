from transformers import pipeline
import re

nlp= pipeline("text-classification",model="sidebert/sentiment-roberta-large-english")
classifier= pipeline('zero-shot-classification',model="facebook/bark-large-mnli")
def detect_sentiments(tweet):
    sentences_tweet_sample=tweet
    sentiments= nlp(sentences_tweet_sample)
    return sentiments

def labelling(tweet):
    candidate_labels= ['loyalty','website','payments','booking','mobile']
    return classifier(tweet,candidate_labels)

def tech_cat(tweet):
    ife_regex = r"(?i)\b(screen|touchscreen|monitor|headphone|earphone|jack|audio|video|movie|tv|wifi|internet|lag|glitch|crash|freezing|unresponsive|black screen|no sound|low volume|entertainment system|IFE|in-flight entertainment|game|usb port|charging port|website|landing page)\b"
    if not re.search(ife_regex, tweet):
        return False
    else:
        return True



if __name__ == "__main__":
    tweet="hi, I am a loyal customer of X.com"
    print(detect_sentiments(tweet))