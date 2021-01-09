from textblob import TextBlob
#uses coleman liau algorithm for readability
def subjectivity_and_grade(article):
    blob = TextBlob(article)
    sentences = len(blob.sentences)
    words = blob.words
    characters = 0
    for word in words:
        characters += len(word)
    if len(words) == 0:
        words.append('a')
    return blob.sentiment.subjectivity, (0.0588 * 100 * (characters / len(words)) - 0.296 * 100 * (sentences / len(words)) - 15.8), blob.sentiment.polarity
