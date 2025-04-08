from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import collections.abc
collections.Hashable = collections.abc.Hashable


chatbot = ChatBot(
    "BeBot",
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I want to help you. Could you please rephrase your question?',
            'maximum_similarity_threshold': 0.65
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

trainer = ListTrainer(chatbot, show_training_progress=False)
greetings = [
    ["hi", "Hello! I'm Bebo, your virtual shopping assistant. How can I help you today?"],
    ["hello", "Hi there! I'm Bebo, ready to help you find the perfect sneakers. What can I do for you?"],
    ["hey", "Hey! I'm Bebo, your sneaker expert. What are you looking for today?"],
    ["good morning", "Good morning! I'm Bebo, here to help with all your sneaker needs. How can I assist you?"],
    ["good afternoon", "Good afternoon! I'm Bebo, your virtual shopping assistant. What can I help you find?"],
    ["good evening", "Good evening! I'm Bebo, ready to help you with anything you need. What are you looking for?"]
]

for greeting in greetings:
    trainer.train(greeting)

print("BeBot is Here! How can I help you today? Type 'exit' to close.")
while True:
    question = input("You: ")
    if question.lower() == "exit":
        break
        
    try:
        response = chatbot.get_response(question)
        print("BeBot:", response)
    except Exception as e:
        print("BeBot: Sorry, I encountered an error. Please try again.")

