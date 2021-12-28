import os
import csv
import json
import nltk
import spacy
import shutil
import gcloud
import logging
import requests
import matplotlib
import numpy as np
import pandas as pd
import urllib.request
import networkx as nx
import src.help_NER_UB
from PIL import Image
from spacy import displacy
from tqdm.notebook import *
from bs4 import BeautifulSoup
from itertools import groupby
from spacy.tokens import Span
import matplotlib.pyplot as plt
from newsapi import NewsApiClient
from spacy.matcher import Matcher
from matplotlib.pyplot import figure
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from stanfordcorenlp import StanfordCoreNLP
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from src.subject_verb_object_extraction import printDeps, extract_link
nlp = spacy.load("en_core_web_sm")


# Scrap Data from a BBC climate article
def scrap_one_article(url, _, nbr_articles):
    # creating an Images directory
    try:
        dirName = 'images'
        os.mkdir(dirName)
    except:
        pass
    url_clean = url

    # cleaning the URL
    if url[6:19] == url[26:39]:
        url_clean = url[19:]
        print(url_clean)
    response = requests.get(url_clean)

    # Generating a bs4 instance
    soup = BeautifulSoup(response.text, 'lxml')
    author = 'BBC News'
    title = None
    csv_writer.writerow(['id', 'url', 'author', 'article_content', 'images descriptions'])

    # Fetching Data from about articles form Html Elements, returning default values if it was not found.
    try:
        author = soup.find_all(class_='ssrcss-1rv0moy-Contributor')[0].find('strong').text[3:]
    except:
        pass
    try:
        title = soup.find_all(class_='ssrcss-gcq6xq-StyledHeading')[0].text
    except:
        pass
    try:
        date = soup.find_all(class_='ecn1o5v2')[0].find('time')['datetime'][:10]
    except:
        date = None
    try:
        cathegory = soup.find_all(class_='ed0g1kj0')[0].text
    except:
        cathegory = 'General'
    Content_list = soup.find_all(class_='eq5iqo00')
    article_content = build_text(Content_list)
    if article_content[:28] == 'This video can not be played':
        article_content = article_content[29:]
    Images_descriptions = download_images_description(soup)
    print('Article ', _, '/', nbr_articles, ' - ', f'[{date}] [{cathegory}][{author}].')

    # Zippping the srapped info into a dict
    article_dic = {'id': _, 'url': url_clean, 'author': author, 'date': date, 'cathegory': cathegory, 'title': title,
                   'article_content': article_content, 'Image count': len(Images_descriptions),
                   'images descriptions': Images_descriptions}
    return article_dic

def build_text(list_):
    list_.pop()
    return '\n'.join([x.text for x in list_])
def dl_img(url, file_path, file_name):
    full_path = file_path + file_name + '.jpg'
    urllib.request.urlretrieve(url, full_path)
    return full_path
def download_images(soup_result,article_index,nbr_articles):
    nbr_img = 0
    try:
        os.mkdir(f'images/Article{article_index}')
    except:
        pass
    img_results = [res['src'] for res in soup_result.find_all('img')][-12:]
    print(len(img_results))
    for _ in tqdm (range(1,len(img_results))):
        image_link = img_results[_]
        image_link_loc = f'images/Article{article_index}/'
        file_name = f'img{_}'
        try:
            image_link_local = dl_img(image_link,image_link_loc, file_name)
            i += 1
            nbr_img+=1
        except:
            pass
        return nbr_img
def download_images_description(soup_result):
    nbr_img = 0
    try:
        os.mkdir(f'images/Article{article_index}')
    except:
        pass
    img_results = [res['alt'] for res in soup_result.find_all('img')][-12:]
    img_results
    return img_results
def get_links_list(soup):
        results = soup.find_all('a',class_ = 'qa-heading-link')
        links_list = ['http://www.bbc.com/'+res['href'] if (res['href'][6:19] != res['href'][26:39]) else res['href'] for res in results]
        return links_list


def scrap_bbc_articles(category_url):
    try:
        shutil.rmtree('images')
    except:
        pass
    url = category_url
    response = requests.get(url)
    print('Request status (200 means a succesful request): ',response.status_code)
    soup = BeautifulSoup(response.text, 'lxml')
    links = get_links_list(soup)
    print('fetching begun ...')
    print('Fetching data from ',len(links) - 5 ,' bbc news articles')
    results = []
    print('------------------------------------')
    for _ in tqdm(range(1,len(links)-5), desc = 'Fetching articles'):  # Covers all the articles len(links)+1
        try:
            A = scrap_one_article(links[_], _, len(links))
            results.append(A)
        except:
            pass
    return results

climate_url = 'https://www.bbc.com/news/science-environment-56837908'
data = scrap_bbc_articles(climate_url)
def fetch_clean_data(data_list):
    article_results = []
    for i in range(len(data_list)):
        try:
            article_dict = {}
            article_dict['id'] = data_list[i]['id']
            article_dict['cathegory'] = data_list[i]['cathegory']
            article_dict['author'] = data_list[i]['author']
            article_dict['title'] = data_list[i]['title']
            article_dict['Publish date'] = data_list[i]['date']
            article_dict['url'] = data_list[i]['url']
            article_dict['article_content'] = data_list[i]['article_content'].strip("\n").strip("\t")
            article_dict['images descriptions'] = data_list[i]['images descriptions']
            article_results.append(article_dict)
        except IndexError:
            pass
    return article_results

Data = pd.DataFrame.from_dict(fetch_clean_data(data))
pd.set_option('max_colwidth', 500)
pd.set_option('max_colwidth', 100)
data_unclean = Data.copy()

Data.to_csv('exported_bbc_data.csv')
Data.to_excel('exported_bbc_data.xlsx')

def clean(Data):
    #lower case all content
    #removing punctuation
    Data["Publish date"].fillna( method ='ffill', inplace = True) # Fill NaN values
    return Data
Data = clean(Data)

index = 4
str_ = str(data_unclean.iloc[index]['article_content']) # Article sample

nlp = spacy.load("en_core_web_sm")
doc = nlp(str_)
entities = []
labels = []
position_start = []
position_end = []
for ent in doc.ents:
    entities.append(ent)
    labels.append(ent.label_)
    position_start.append(ent.start_char)
    position_end.append(ent.end_char)
data_entities_2 = pd.DataFrame({'Entities':entities,'Labels':labels,'Position_Start':position_start, 'Position_End':position_end})



java = "C:/Program Files/Java/jre1.8.0_311/bin/java.exe"
os.environ["JAVAHOME"] = java
annotators= 'tokenize,ssplit,pos,lemma,ner,parse,depparse,sentiment',
os.environ["CORENLP_HOME"] = "D:/stanford-corenlp-4.3.2/stanford-corenlp-4.3.2.jar/stanford-corenlp-4.3.2/stanford-corenlp-4.3.2.jar"
nlp = StanfordCoreNLP('http://localhost', port=9000,timeout=30000)
text = str_
nlp_results = nlp.annotate(text,properties={
        'annotators':'sentiment, ner, pos',
        'outputFormat': 'json',
        'timeout': 50000,
        })
json_results = json.loads(nlp_results)
sentiment_description = json_results['sentences'][0]['sentiment']
sentiment_value = json_results['sentences'][0]['sentimentValue']
print('sentiment analysis : ',sentiment_description, sentiment_value)


#fetch for results using a google api.
def NE_info_fetch(named_entity):
    url = "https://google-search26.p.rapidapi.com/search"
    Ne = named_entity
    querystring = {"q":Ne,"hl":"en","tbs":"qdr:a",'as_sitesearch':'wikipedia.com'}

    headers = {
        'x-rapidapi-host': "google-search26.p.rapidapi.com",
        'x-rapidapi-key': "ea42e2dcc0msh49ecba51860383ep18d94ejsnbb0488e12e70"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    try:
        return (response.json()['results'][0]['snippet'][:200])
    except IndexError :
        return 'Wikipedia'



def get_summary(named_entity,data_unclean,_):
    def sumarize(List):
        result = []
        for _ in List:
            url = "https://api.meaningcloud.com/summarization-1.0"
            querystring = {"txt":_,"of":"json",'key':'1fe6342e2cfafb085d01802a50c98e6d','limit': 10}
            response = requests.request("GET", url, params=querystring)
            result.append(response.json()['summary'])
        return result
    text = str(data_unclean.iloc[index]['article_content'])
    phrases = nltk.tokenize.sent_tokenize(text)
    results = []
    for _ in range(len(phrases)):
        if named_entity in phrases[_]:
            results.append(phrases[_])
            if _ < len(phrases):
                #return two phrases instead of one, to give more information about thenamed entity
                results.append(phrases[_ + 1])
    return sumarize(results)
get_summary('Shuck', data_unclean,index)
get_info = lambda x: [get_summary(x,data_unclean,index),NE_info_fetch(x)]

info = data_entities_2[["Entities",'Labels']]
df_result = pd.DataFrame(columns = ['Entities','Labels','Text'])
for _ in tqdm(info.iterrows()):
    #it doesn't append idk whyn
    #don't forget that the output of get info return a list of two list, its not a string , trying using another thing than iloc
    info = get_info(_[1]['Entities'])
    df_result = df_result.append(pd.DataFrame.from_dict({'Entities':_[1]['Entities'], 'Labels': _[1]['Labels'],'summary':info[0],'image description': info[1] }) , ignore_index=True)

if __name__ == '__main__':
    print('Module imported succesfully')