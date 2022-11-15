# jaccard similarity scorer (for now)
def getJaccardScore(str1_tokens, str2_tokens):
    a = set(str1_tokens)
    b = set(str2_tokens)
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))
