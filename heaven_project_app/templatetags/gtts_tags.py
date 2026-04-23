from django import template
from gtts import gTTS
from django.conf import settings
import os
import hashlib


register = template.Library()

@register.simple_tag
def say(lang, text, page="default"):
    # Generates Text To Speech MP3 to give text and returns media URL.
    # Hash used to avoid regenerating same text multiple times
    
    # Creating folder for a page
    page_folder = os.path.join(settings.MEDIA_ROOT, page, lang)
    os.makedirs(page_folder, exist_ok = True)

    # Hashing filename and joining file paths.
    filename = hashlib.md5(text.encode('utf-8')).hexdigest() + ".mp3"
    filepath = os.path.join(page_folder, filename)
    
    # Generate if it is missing.
    if not os.path.exists(filepath):
        tts = gTTS(text=text, lang=lang)
        tts.save(filepath)
    
     # Return proper URL for HTML
    return f"{settings.MEDIA_URL}{page}/{lang}/{filename}"