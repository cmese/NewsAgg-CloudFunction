from nltk.corpus import stopwords
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer

# filters a raw string into its most 'meaningful' tokens

stop_words = set(stopwords.words('english'))
ps_stem = PorterStemmer()
sb_stem = SnowballStemmer(language='english')
lemma = WordNetLemmatizer()

def lowerCase(words):
    return [word.lower() for word in words]

# removes stop words and puncuation from a string
def removeStopWords(words):
    return [word for word in words if not word in stop_words]

def removePunc(words):
    return [word for word in words if word.isalnum()]

#unused for now
def removeNonAlpha(words):
    return [word for word in words if word.isalpha()]


# might be overkill, especially for keyword list
# might be good, groups words into one root word for more accurate comparisons
# stem vs snowballStem vs lematize instead?
    # https://towardsdatascience.com/stemming-vs-lemmatization-2daddabcb221
# PorterStemmer
def stemmer(words):
    return [ps_stem.stem(word) for word in words]


# SnowballStemmer
def sb_stemmer(words):
    return [sb_stem.stem(word) for word in words]


# Lemmatizer
def lematizer(words):
    return [lemma.lemmatize(word) for word in words]


def filterString(raw_string):
    tokenized_string = word_tokenize(raw_string)
    # print(tokenized_string)
    # print("-----------")
    lc_string = lowerCase(tokenized_string)
    # print(lc_string)
    # print("-----------")
    no_punc_string = removePunc(lc_string)
    # print(no_punc_string)
    # print("-----------")
    no_sw_string = removeStopWords(no_punc_string)
    # print(no_sw_string)
    # print("-----------")
    # filtered_string = lematizer(no_sw_string)
    # TODO: Remove non alpha words?
    return no_sw_string
