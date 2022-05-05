from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from nltk.corpus import stopwords
import pickle
import json
import random
from tensorflow.python.framework import ops
import tensorflow
import tflearn
import numpy as np

import re
# Chat Bot Libs.......................
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
stop_words = set(stopwords.words('english'))

# Done .......................

# Data & Model TRain---------------------------------


def get_file_data(data, stop_word_removal='no', train='yes'):
    file_contents = data
    text = []
    if train == 'yes':
        for val in file_contents:
            sent = re.findall("[A-Za-z]+", val)
            line = ''
            for words in sent:

                if stop_word_removal == 'yes':
                    if len(words) > 1 and words not in stop_words:
                        line = line + ' ' + words
                else:
                    if len(words) > 1:
                        line = line + ' ' + words
            text.append(line)

    else:
        for val in file_contents.split('.'):
            sent = re.findall("[A-Za-z]+", val)
            line = ''
            for words in sent:

                if stop_word_removal == 'yes':
                    if len(words) > 1 and words not in stop_words:
                        line = line + ' ' + words
                else:
                    if len(words) > 1:
                        line = line + ' ' + words       
            text.append(line)    
    return text


def generate_dictinoary_data(text):
    word_to_index = dict()
    index_to_word = dict()
    corpus = []
    count = 0
    vocab_size = 0

    for row in text:
        for word in row.split():
            word = word.lower()
            corpus.append(word)
            if word_to_index.get(word) == None:
                word_to_index.update({word: count})
                index_to_word.update({count: word})
                count += 1
    vocab_size = len(word_to_index)
    length_of_corpus = len(corpus)

    return word_to_index, index_to_word, corpus, vocab_size, length_of_corpus


def get_one_hot_vectors(target_word, context_words, vocab_size, word_to_index):

    trgt_word_vector = np.zeros(vocab_size)

    index_of_word_dictionary = word_to_index.get(target_word)

    trgt_word_vector[index_of_word_dictionary] = 1

    ctxt_word_vector = np.zeros(vocab_size)

    for word in context_words:
        index_of_word_dictionary = word_to_index.get(word)
        ctxt_word_vector[index_of_word_dictionary] = 1

    return trgt_word_vector, ctxt_word_vector


def generate_training_data(corpus, window_size, vocab_size, word_to_index, length_of_corpus, sample=None):

    training_data = []
    training_sample_words = []
    for i, word in enumerate(corpus):

        index_target_word = i
        target_word = word
        context_words = []

        if i == 0:

            context_words = [corpus[x] for x in range(i + 1, window_size + 1)]

        elif i == len(corpus)-1:

            context_words = [corpus[x] for x in range(
                length_of_corpus - 2, length_of_corpus - 2 - window_size, -1)]

        else:

            before_target_word_index = index_target_word - 1
            for x in range(before_target_word_index, before_target_word_index - window_size, -1):
                if x >= 0:
                    context_words.extend([corpus[x]])

            after_target_word_index = index_target_word + 1
            for x in range(after_target_word_index, after_target_word_index + window_size):
                if x < len(corpus):
                    context_words.extend([corpus[x]])

        trgt_word_vector, ctxt_word_vector = get_one_hot_vectors(
            target_word, context_words, vocab_size, word_to_index)
        training_data.append([trgt_word_vector, ctxt_word_vector])

        if sample is not None:
            training_sample_words.append([target_word, context_words])

    return training_data, training_sample_words


with open("./media/New_Json_norm.json") as file:
    data = json.load(file)

try:
    with open("data.pickle", "rb") as f:
        training_data, training_sample_words, word_to_index, index_to_word, corpus, vocab_size, length_of_corpus, window_size = pickle.load(
            f)
except:
    t = []
    for intent in data['intents']:
        for question in intent['question']:
            t.append(question)

    text = get_file_data(t, 'yes')
    word_to_index, index_to_word, corpus, vocab_size, length_of_corpus = generate_dictinoary_data(
        text)
    window_size = 2
    training_data, training_sample_words = generate_training_data(
        corpus, window_size, vocab_size, word_to_index, length_of_corpus, 'yes')

    with open("data.pickle", "wb") as f:
        pickle.dump((training_data, training_sample_words, word_to_index,
                     index_to_word, corpus, vocab_size, length_of_corpus, window_size), f)

ops.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training_data[0][1])])
net = tflearn.fully_connected(net, len(training_data[0][1]), activation="elu")
net = tflearn.fully_connected(net, len(training_data[0][1]), activation="elu")
net = tflearn.fully_connected(net, len(training_data[0][1]), activation="elu")
net = tflearn.fully_connected(net, len(training_data[0][1]), activation="elu")
net = tflearn.fully_connected(
    net, len(training_data[0][0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    model.load("./model.tflearn")
except Exception as e:
    model.fit(training_data[:][1], training_data[:][0],n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")
# Chat---------------------------------


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


# Done ........................

@csrf_exempt
def Talk(request):
    response = {'status': None}

    if request.method == 'POST':
        da = json.loads(request.body)
        mesg = da['message']
        print("\n")
        print(mesg)
        print("\n")
        # chat_response = "Hello Python"
        user_input = str(mesg)
        if user_input.lower() == 'quit' or user_input.lower() == 'close':
            return render(request, "home.html", {'title': 'Sili Chatbot Version 1.0'})
        else:
            text = get_file_data(user_input, stop_word_removal='yes', train='no')
            _, _, corpus_, _, length_of_corpus_ = generate_dictinoary_data(
            text)
            window_size = 2
            predict_data_, predict_sample_words = generate_training_data(
            corpus_, window_size, vocab_size, word_to_index, length_of_corpus_, 'yes')
            results = model.predict(predict_data_[:][1])

            print(results[0])

            results_index = np.argmax(results[1])
            print(results_index)
            # print(results_index)
            # tag = labels[results_index]
            # print(tag)
            for tg in data["intents"]:
                if tg['question'] == tag:
                    responses = tg['responses']

            print(random.choice(responses))
            chat_response = str(random.choice(responses))
            # chat_response = BankBot.get_response(user_input)
        print(chat_response)
        response['message'] = {'text': str(
            chat_response), 'user': False, 'chat_bot': True}
        response['status'] = 'ok'
    else:
        response['error'] = 'no post data found'

    return HttpResponse(
        json.dumps(response),
        content_type="application/json")


def home(request):
    return render(request, "home.html", {'title': 'Sili Chatbot Version 1.0'})
