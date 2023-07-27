from nltk.corpus import stopwords
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer

import string

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

    no_num_string = removeNonAlpha(no_sw_string)
    # print(no_sw_string)
    # print("-----------")
    # filtered_string = lematizer(no_sw_string)
    # TODO: Remove non alpha words?
    return no_num_string

def filterString2(raw_string):

    # convert to lowercase
    new_text = raw_string.lower()

    # remove punctuation 
    new_text = new_text.translate(str.maketrans('', '', string.punctuation))

    # tokenize
    tokens = word_tokenize(new_text)

    # remove stopwords and number tokens and lemmatize them
    processed_text = [lemma.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]

    # convert back into a single string
    processed_text = ' '.join(processed_text)

    return processed_text

def filter_string3(preprocessed_string):
    translator = str.maketrans('', '', string.punctuation)

    # Remove non-alphabetic characters and punctuation, and convert to lowercase
    cleaned_text = preprocessed_string.translate(translator).lower()

    return cleaned_text

def process_text(row):
    print("trying to process text.............")
    title = row['title']
    text = row['text']
    description = row['description']

    combined_text = f'{title} {text} {description}'

    # convert to lowercase
    combined_text = combined_text.lower()

    # remove punctuation 
    combined_text = combined_text.translate(str.maketrans('', '', string.punctuation))

    # tokenize
    tokens = word_tokenize(combined_text)

    # remove stopwords and number tokens and lemmatize them
    processed_text = [lemma.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]

    # convert back into a single string
    processed_text = ' '.join(processed_text)

    return processed_text

