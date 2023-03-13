import numpy as np
import pandas as pd
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from pathlib import Path  

dfAbusive = pd.read_csv('data/abusive.csv', encoding = 'latin-1')
def delete_abusive(text):
    # Convert the DataFrame to a dictionary
    words_to_delete = dict(zip(dfAbusive['ABUSIVE'], [''] * len(dfAbusive)))
    
    # Construct the regular expression pattern
    pattern = '|'.join(r'\b{}\b'.format(re.escape(word)) for word in words_to_delete.keys())
    
    # Delete the matched words in the text
    return re.sub(pattern, '', text)

dfStopword = pd.read_csv('data/stopwordbahasa.csv', header=None)
dfStopword = dfStopword.rename(columns={0: 'stopword'})

dfAlay = pd.read_csv('data/new_kamusalay.csv', header=None, encoding = 'latin-1')
mapAlay = dict(zip(dfAlay[0], dfAlay[1]))
dfAlayDict = dfAlay.set_index(0).to_dict()
alayDict = dfAlayDict[1]

factory = StemmerFactory()
stemmer = factory.create_stemmer()

def lowercase(text):
    return text.lower()

def remove_unnecessary_char(text):
    text = re.sub('\n',' ',text) # Remove every '\n'
    text = re.sub('rt',' ',text) # Remove every retweet symbol
    text = re.sub('user',' ',text) # Remove every username
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # Remove every URL
    text = re.sub('  +', ' ', text) # Remove extra spaces
    return text
    
def remove_nonaplhanumeric(text):
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
    return text

def normalize_alay(text):
    return ' '.join([mapAlay[word] if word in mapAlay else word for word in text.split(' ')])

def remove_stopword(text):
    text = ' '.join(['' if word in dfStopword.stopword.values else word for word in text.split(' ')])
    text = re.sub('  +', ' ', text) # Remove extra spaces
    text = text.strip()
    return text

def stemming(text):
    return stemmer.stem(text)

def preprocess(text):
    text = lowercase(text) # 1
    text = remove_nonaplhanumeric(text) # 2
    text = remove_unnecessary_char(text) # 3
    text = normalize_alay(text) # 4
    text = stemming(text) # 5
    text = remove_stopword(text) # 6
    return text

def replace_alay(text):
    pattern = '|'.join(r'\b{}\b'.format(re.escape(word)) for word in alayDict.keys())
    return re.sub(pattern, lambda m: alayDict[m.group(0)], text)

def process_text(text):
    text = preprocess(text)
    text = replace_alay(text)
    text = delete_abusive(text)
    
    return text


def process_file(file,col_num):
    dfData = pd.read_csv(file, encoding = 'latin-1')

    dfData[dfData.columns[col_num]] = dfData[dfData.columns[col_num]].apply(preprocess)
    dfData = dfData.drop_duplicates()
    
    dfData[dfData.columns[col_num]] = dfData[dfData.columns[col_num]].apply(lambda x: replace_alay(x))
    dfData[dfData.columns[col_num]] = dfData[dfData.columns[col_num]].apply(lambda x: delete_abusive(x))

    filepath = Path('output/out.csv')  
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    dfData.to_csv(filepath)