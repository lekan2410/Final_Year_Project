# https://www.geeksforgeeks.org/nlp/building-a-rule-based-chatbot-with-natural-language-processing/

import nltk
import re
from nltk.chat.util import Chat, reflections

pairs = [
    [r"hi|hello|hey", ["Hello! How can I help you today?",
                       "Hi there! How may I assist you?"]],
    [r"my name is (.*)", ["Hello %1! How can I assist you today?"]],
    [r"(.*) your name?", ["I am your friendly chatbot!"]],
    [r"how are you?", ["I'm just a bot, but I'm doing well. How about you?"]],
    [r"tell me a joke", ["Why don't skeletons fight each other? They don't have the guts!"]],
    [r"(.*) (help|assist) (.*)", ["Sure! How can I assist you with %3?"]],
    [r"bye|exit", ["Goodbye! Have a great day!", "See you later!"]],
    [r"(.*)", ["I'm sorry, I didn't understand that. Could you rephrase?",
               "Could you please elaborate?"]]
]

class RuleBasedChatbot:
    def __init__(self, pairs):
        self.chat = Chat(pairs, reflections)

    def respond(self, user_input):
        return self.chat.respond(user_input)
