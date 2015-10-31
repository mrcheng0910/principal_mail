from bs4 import BeautifulSoup
from urllib2 import urlopen
import unicodedata
import string

urls = {}
urls['senza'] = "http://www.tripadvisor.com/Hotel_Review-g32766-d190271-Reviews-orASDF0-Senza_Hotel-Napa_Napa_Valley_California.html#REVIEWS"
urls['parisian'] = "http://www.tripadvisor.com/Hotel_Review-g34439-d267917-Reviews-orASDF0-Parisian_Hotel_Suites-Miami_Beach_Florida.html#REVIEWS"
hotels = urls.keys()
class Review_object():

    ''' Class for storing review content.
        Unsure how many attributes I'll
        collect here...we'll start with
        text content and an index '''

    def __init__(self, content, idx):
        self.content = content
        self.idx = idx


def make_soup(url):
    r = urlopen(url).read()
    soup = BeautifulSoup(r)
    return soup


def remove_punctuation(input_string):

    ''' I'm only interested in the
    word content. Not the punctuation.
    I also need to handle unicode. We'll
    convert unicode to ascii here and strip
    punctuation. '''

    exclude = set(string.punctuation)
    try:
        s = input_string.replace('\t', ' ').replace('\n', ' ').replace('-', ' ')
    except:
        # unsure why this is occasionally necessary
        s = ''.join(xx for xx in input_string.contents)
        s = s.replace('\t', ' ').replace('\n', ' ').replace('-', ' ')

    s = ''.join(ch for ch in s if ch not in exclude)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    s = ''.join(ch for ch in s if ch.isalpha() or ch==' ')
    return s.lower()


def dump_data(data, hotel_name):
    ''' Save data to file. '''
    url = urls[hotel_name]
    outfile = open('dump_' + hotel_name + '.csv', 'w')
    outfile.write(url + '\n')
    for each_object in data:
        content = remove_punctuation(each_object.content)
        outfile.write(str(each_object.idx) + ',' + content + '\n')
    outfile.close()


data_dictionary = {}
for each_hotel in hotels:
    global_index = 0
    print "\nScraping",each_hotel,"reviews."
    # first, let's see how many pages of reviews exist
    soup = make_soup(urls[each_hotel].replace('ASDF','0'))
    page_links = [xx.attrs for xx in soup.find_all('a') if 'data-page-number' in xx.attrs.keys()]
    pages = [int(xx['data-page-number']) for xx in page_links]
    print "Tripadvisor contains",max(pages),"pages of reviews for this hotel."

    # now we'll iterate through each page
    data = []
    for ii in range(max(pages)+1):
        print ii,
        url = urls[each_hotel].replace('ASDF', str(ii))
        soup = make_soup(url)
        # find all review titles
        titles = [xx.contents[0] for xx in
                  soup.find_all("span", class_="noQuotes")]
        # find all review entries
        pentries = [xx.contents[0] for xx in
                    soup.find_all("p", class_="partial_entry")]
        # add to dataset
        for eachtitle in titles:
            data.append(Review_object(eachtitle, global_index))
            global_index += 1
        for eachentry in pentries:
            if len(eachentry) > 2:
                data.append(Review_object(eachentry, global_index))
                global_index += 1

    print "\nFinished analyzing " + each_hotel
    data_dictionary[each_hotel] = data
    print "Saving data to dump_%s.csv." % (each_hotel)
    dump_data(data, each_hotel)
from nltk.corpus import wordnet as wn
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

datafiles = ['dump_'+xx+'.csv' for xx in hotels]
excludedwords = ['room','hotel','motel']
wordcount = pd.DataFrame()

for eachfile in datafiles:
    infile = open(eachfile,'r')
    words = []
    # Let's clean the data a bit by removing numbers
    for eachline in infile:
        linewords = [xx.lower() for xx in eachline.split(' ')]
        for eachword in linewords:
            words.append(''.join(ch for ch in eachword if ch.isalpha()))
    words = [xx for xx in words if xx not in excludedwords]
    words_unique = np.unique(words)


    # Now we'll filter by parts of speech
    adjectives = []
    for eachword in words_unique:
      ss = wn.synsets(eachword)
      if len(ss) > 0:
        pos = [xx.pos() for xx in ss]
        if 's' in pos:
          adjectives.append(eachword)

    # Generate some word clouds
    all_adjectives = [xx for xx in words if xx in adjectives]

    wc = WordCloud(background_color="white", margin=5, width=600, height=300)
    wc2 = WordCloud(background_color="white", margin=5, width=600, height=300)
    if 'isian' in eachfile:
        wc2 = WordCloud(background_color="black", margin=5, width=600, height=300)
    wordcloud = wc.generate(' '.join(words))
    adjectivecloud = wc2.generate(' '.join(all_adjectives))

    # Print top ten
    print eachfile
    wordcount['all_' + eachfile] = [xx[0] for xx in wordcloud.words_[0:10]]
    wordcount['adj_' + eachfile] = [xx[0] for xx in adjectivecloud.words_[0:10]]

    plt.imshow(wordcloud)
    plt.title(eachfile[0:-4].replace('dump_','') + ' all')
    plt.axis("off")
    plt.savefig(eachfile[0:-4] + '_all.png',dpi=600)
    plt.clf()

    plt.imshow(adjectivecloud)
    plt.title(eachfile[0:-4].replace('dump_','') + ' adjectives')
    plt.axis("off")
    plt.savefig(eachfile[0:-4] + '_adjectives.png',dpi=600)
    plt.clf()