from flask import Flask, request, jsonify, render_template
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.logic import BestMatch, LogicAdapter
from chatterbot.response_selection import get_most_frequent_response
import collections.abc
import sys
import json

collections.Hashable = collections.abc.Hashable

class CustomLogicAdapter(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        return True

    def process(self, input_statement, additional_response_selection_parameters=None):
        import random
        from chatterbot.conversation import Statement

        
        fallback_responses = [
            "I understand you're asking about {}, but could you please provide more details so I can better assist you?",
            "I want to help you with {}, could you elaborate a bit more?",
            "I'm here to help with {}. Could you rephrase your question?",
            "Let me help you with {}. Could you give me more specific information?",
            "I'd be happy to assist with {}. What exactly would you like to know?"
        ]

    
        response = self.chatbot.storage.get_random()
        
        
        if response.confidence < 0.5:
            
            keywords = [word for word in input_statement.text.lower().split() if len(word) > 3]
            if keywords:
                topic = keywords[0]  
                response.text = random.choice(fallback_responses).format(topic)
                response.confidence = 0.5
            else:
                response.text = "I'm here to help! Could you please rephrase your question?"
                response.confidence = 0.5

        return response


chatbot = ChatBot(
    "BeBot",
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I want to help you. Could you please rephrase your question?',
            'maximum_similarity_threshold': 0.65,
            'response_selection_method': get_most_frequent_response
        },
        {
            'import_path': __name__ + '.CustomLogicAdapter'
        }
    ],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
        'chatterbot.preprocessors.unescape_html',
        'chatterbot.preprocessors.convert_to_ascii'
    ],
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.sqlite3'
)


list_trainer = ListTrainer(chatbot, show_training_progress=False)
corpus_trainer = ChatterBotCorpusTrainer(chatbot, show_training_progress=False)


greetings = [
    ["hi", "Hello! I'm Bebo, your virtual shopping assistant. How can I help you today?"],
    ["hello", "Hi there! I'm Bebo, ready to help you find the perfect sneakers. What can I do for you?"],
    ["hey", "Hey! I'm Bebo, your sneaker expert. What are you looking for today?"],
    ["good morning", "Good morning! I'm Bebo, here to help with all your sneaker needs. How can I assist you?"],
    ["good afternoon", "Good afternoon! I'm Bebo, your virtual shopping assistant. What can I help you find?"],
    ["good evening", "Good evening! I'm Bebo, ready to help you with anything you need. What are you looking for?"]
]


for greeting in greetings:
    list_trainer.train(greeting)


corpus_trainer.train(
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations",
    "my_corpus/customer_service.yml",
    "my_corpus/virtual_assistant.yml"
)

def get_chatbot_response(question):
    try:
    
        response = chatbot.get_response(question)
        
        
        if response.confidence < 0.5:
            keywords = [word for word in question.lower().split() if len(word) > 3]
            if keywords:
                
                keyword_response = chatbot.get_response(" ".join(keywords))
                if keyword_response.confidence > response.confidence:
                    response = keyword_response

        return str(response)
    except Exception as e:
        return "I apologize, but I'm having trouble processing your request. Could you please rephrase your question?"

if __name__ == "__main__":
    if len(sys.argv) > 1:
      
        question = sys.argv[1]
        response = get_chatbot_response(question)
        print(response)
    else:
      
        app = Flask(__name__)

        @app.route("/")
        def home():
            return render_template("index.html")

        @app.route("/ask", methods=["POST"])
        def ask():
            user_input = request.json.get("question")
            if not user_input:
                return jsonify({"error": "Question not provided"}), 400

            response = get_chatbot_response(user_input)
            return jsonify({"answer": response})

        app.run(debug=True)
