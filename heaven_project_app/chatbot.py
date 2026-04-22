# https://www.geeksforgeeks.org/nlp/building-a-rule-based-chatbot-with-natural-language-processing/

import nltk
import re
from nltk.chat.util import Chat, reflections

pairs = [
     [r"hi|hello|hey|yo", ["Hello! How can I help you today?",
                         "Hi there! How may I assist you?"]],
     [r"my name is (.*)", ["Hello %1! How can I assist you today?"]],
     [r"(.*) your name?", ["I am your friendly chatbot!"]],
     [r"how are you?", ["I'm just a bot, but I'm doing well. How about you?"]],
     [r"tell me a joke", ["Why don't skeletons fight each other? They don't have the guts!",
                         "Can a horse join the army, no the Neigh-vy",
                         "What did the cop say to his belly button?, You're under a vest!",]],
     [r"help|assist", ["Sure! here are the things I can do, <br><br> I can search for the nearest locations on shelters, "
     "food banks and support services<br><br>, I can tell you information on a specific service<br><br> send you links to specific pages on the website<br><br> use 'Commands' to find more information and remember i'm still in development."]],
     [r"bye|exit", ["Goodbye! Have a great day!", "See you later!"]],
     [r"i'm fine|i'm great|im great|im fine", ["That's great to hear!", "Wow that's wonderful to hear!"]],
     [r"How does this website help?", ["This website helps to allow people to find services to support those who are experincing homelessness"]],
     [r"What can you do?", ["I can answer questions, help you find services and tell jokes!"]],
     

     [r"where can i find nearest shelter?|where can i find shelters?| nearest shelters", ["SHOW_NEAREST_SHELTERS"]],
     [r"where can i find nearest food bank?|where can i find food banks?", ["SHOW_NEAREST_FOODBANKS."]],
     [r"where can i find nearest support service?|where can i find support services?", ["SHOW_NEAREST_SUPPORTS_SERVICES."]],

     [r"general information", ["This is a website that helps those who are experiencing homeless or people that are vulnerable to find services to support them. Food banks, Shelters and Support Services available. "]],

     [r"features|feature", ["Users can leave reviews on services, <br><br> - edit their profile and use me to find out more information, <br><br> - navigate the website or use me to tell jokes!"]],
     
     [r"(commands)", ["Here are some things you can type:<br><br>"
               "- 'nearest food bank/nearest shelter/nearest support service?'<br><br>"
               "- 'specific food bank/specific shelter/ specific support service"
               "- 'Where can I find support services?'<br><br>"
               "- 'Tell me a joke'<br><br>"
               "- 'What can you do?'<br><br>"
               "- 'General information'<br><br>"
               "- 'Features'<br><br>"
               "- 'Help'<br><br>"
               "- 'Limitations on Location'<br><br>"
               "- 'Bye' or 'Exit' to leave the chat<br><br>"
               "You don’t have to type these exactly—I’ll try to understand similar questions too!"]],
     
     [r"Limitations on Location|limitation on location", ["Services available are only based on Cambridge due to early stages of development. <br><br> Use postcodes that are in Cambridge. <br><br> Using other postcodes outside of Cambridge may or may not return nearest results. <br><br> More Services will be available in the future."]],
     
     [r"Specific Food Bank|specific food bank", ["SPECIFIC FOOD BANK"]],

     [r"Specific Shelter|specific shelter", ["SPECIFIC SHELTER"]],

     [r"Specific Support Service|specific support service", ["SPECIFIC FOOD BANK"]],

     [r"(.*)", ["I'm sorry, I didn’t quite understand that.\n\n"
               "You can try things like:<br><br>"
               "- 'Where can I find a shelter?'<br><br>"
               "- 'Nearest Shelter'<br><br>"
               "- Type 'commands' to see all options"]],

     ]


class RuleBasedChatbot:
    def __init__(self, pairs):
        self.chat = Chat(pairs, reflections)

    def respond(self, user_input):
        return self.chat.respond(user_input)
