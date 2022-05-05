import json
from nltk.stem import WordNetLemmatizer
import nltk
import io
import random
import string  # to process standard python strings
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')
nltk.download('popular', quiet=True)


class Chatbot():

    GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
    GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there",
                          "hello", "I am glad! You are talking to me"]

    def __init__(self, file):
        with open(file, 'r', errors='ignore') as json_file:
            self.data = json.load(json_file)

        with open('question.txt', 'w', errors='ignore') as f:
            for i in self.data['intents']:
                f.write('{}\n'.format(i['question'][0].lower()))

        with open('question.txt', 'r', errors='ignore') as question_file:
            self.raw = question_file.read()
            self.raw = self.raw.lower()

        self.sent_tokens = nltk.sent_tokenize(self.raw)
        self.word_tokens = nltk.word_tokenize(self.raw)

        self.lemmer = nltk.stem.WordNetLemmatizer()

        self.remove_punct_dict = dict((ord(punct), None)
                                      for punct in string.punctuation)

    def LemTokens(self, tokens):
        return [self.lemmer.lemmatize(token) for token in tokens]

    def LemNormalize(self, text):
        return self.LemTokens(nltk.word_tokenize(text.lower().translate(self.remove_punct_dict)))

    def greeting(self, sentence):
        for word in sentence.split():
            if word.lower() in Chatbot.GREETING_INPUTS:
                return random.choice(Chatbot.GREETING_RESPONSES)

    def response(self, user_response):
        robo_response = ''
        self.sent_tokens.append(user_response)
        TfidfVec = TfidfVectorizer(
            tokenizer=self.LemNormalize, stop_words='english')
        tfidf = TfidfVec.fit_transform(self.sent_tokens)
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx = vals.argsort()[0][-2]
        flat = vals.flatten()
        flat.sort()
        req_tfidf = flat[-2]
        if(req_tfidf == 0):
            robo_response = robo_response+"No found"
            return robo_response
        else:
            robo_response = robo_response+self.sent_tokens[idx]
            return robo_response

    def give_answer(self, response, isBackup=False):
        for i in self.data['intents']:
            if response == i['question'][0].lower():
                res = i['responses']
                if isBackup:
                    return res[0]
                else:
                    return res[1]
        else:
            return ('No found')

    def backup_response(self, user_response):
        tokens = nltk.word_tokenize(user_response)
        robo_responses = []
        for x in tokens:
            r = self.response(x)
            if r != x and r != user_response:
                robo_responses.append(r)
        return robo_responses
    
    def final_response(self, user_response):
        robo_response = self.response(user_response)
        if robo_response != 'No found':
            answer = self.give_answer(robo_response)
            if answer != 'No found':
                return answer
            else:
                backup = self.backup_response(user_response)
                backup_answer = []
                if len(backup) != 0:
                    for x in backup:
                        backup_answer_x = self.give_answer(x, True)
                        if backup_answer_x != 'No found':
                            backup_answer.append(backup_answer_x)
                    else:
                        if len(backup_answer) != 0:
                            return backup_answer
                        else:
                            return ("Sorry, I can't understand!\nAsk correctly.")
                else:
                    return ("Sorry, I can't understand!\nAsk correctly.")
        else:
            backup = self.backup_response(user_response)
            backup_answer = []
            if len(backup) != 0:
                for x in backup:
                    backup_answer_x = self.give_answer(x, True)
                    if backup_answer_x != 'No found':
                        backup_answer.append(backup_answer_x)
                else:
                    if len(backup_answer) != 0:
                        return (backup_answer)
                    else:
                        return ("Sorry, I can't understand!\nAsk correctly.")
            else:
                return ("Sorry, I can't understand!\nAsk correctly.")

    def ask_question(self, question):

        user_response = question.lower()
        if(user_response != 'bye'):
            if(user_response == 'thanks' or user_response == 'thank you'):
                return ("ROBO: You are welcome..")
            else:
                if(self.greeting(user_response) != None):
                    robo_response = ("ROBO: "+self.greeting(user_response))
                    # self.sent_tokens.remove(user_response)
                    return robo_response
                else:
                    robo_response = self.final_response(user_response)
                    # self.sent_tokens.remove(user_response)
                    return robo_response

        else:
            return ("ROBO: Bye! take care..")


if __name__ == "__main__":
    a = Chatbot('New_Json_norm.json')
    print(a.ask_question('authentication'))
