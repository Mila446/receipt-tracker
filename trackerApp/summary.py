import nltk
import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('stopwords')
nltk.download('punkt')

from heapq import nlargest


def summarize(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)
    freq_table = {}
    # count word frequency
    for word in words:
        word = word.lower()
        if word not in stop_words:
            if word in freq_table:
                freq_table[word]+=1
            else:
                freq_table[word]=1
    sentences = sent_tokenize(text)

    sentence_value = {}

    for sentence in sentences:
        for word, freq in freq_table.items():
            if word in sentence.lower():
                if sentence in sentence_value:
                    sentence_value[sentence] += freq
                else:
                    sentence_value[sentence] = freq

    length = int(len(sentence_value)* 0.5)
    summary = nlargest(length,sentence_value,key = sentence_value.get)
    summary1 = [word for word in summary]
    summary2 = ''.join(summary1)
    summary3=sent_tokenize(summary2)
    final_summary = '\n'.join(summary3)
    return final_summary