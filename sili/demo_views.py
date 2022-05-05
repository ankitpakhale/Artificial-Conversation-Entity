from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer


BankBot = ChatBot(name='BankBot',
                  read_only=False,
                  logic_adapters=["chatterbot.logic.BestMatch"],
                  storage_adapter="chatterbot.storage.SQLStorageAdapter")

corpus_trainer = ChatterBotCorpusTrainer(BankBot)
corpus_trainer.train("chatterbot.corpus.english")

greet_conversation = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]


# Initializing Trainer Object
trainer = ListTrainer(BankBot)

# Training BankBot
trainer.train(greet_conversation)


@csrf_exempt
def Talk(request):
    response = {'status': None}

    if request.method == 'POST':
        data = json.loads(request.body)
        mesg = data['message']
        print("\n")
        print(mesg)
        print("\n")
        # chat_response = "Hello Python"
        user_input = str(mesg)
        if user_input == 'quit' or user_input == 'close':
            return render(request, "home.html", {'title': 'Sili Chatbot Version 1.0'})
        else:
            chat_response = BankBot.get_response(user_input)
        print(chat_response)
        response['message'] = {'text': str(
            chat_response), 'user': False, 'chat_bot': True}
        response['status'] = 'ok'

    else:
        response['error'] = 'no post data found'

    return HttpResponse(
        json.dumps(response),
        content_type="application/json"
    )


def home(request):
    return render(request, "home.html", {'title': 'Sili Chatbot Version 1.0'})
