from django.shortcuts import render

# Create your views here.

import random

quotes = [
    "Where you stand depends on where you sit.",
    "I am the captain of my soul.",
    "There is nothing like returning to a place that remains unchanged to find the ways in which you yourself have altered.",
    "I have taken a moment here to rest, to steal a view of the glorious vista that surrounds me, to look back on the distance I have come. But I can only rest for a moment, for with freedom come responsibilities, and I dare not linger, for my long walk is not ended.",
    "It is said that no one truly knows a nation until one has been inside its jails.",
    "Sometimes it falls upon a generation to be great, you can be that generation.",
    "I have never cared very much for personal prizes. A person does not become a freedom fighter in the hope of winning awards.",
]

images = [
    '/static/images/img1.webp',
    '/static/images/img2.jpeg',
    '/static/images/img3.webp',
    '/static/images/img4.jpg'
]

def quote(request):
    selected_quote = random.choice(quotes)
    selected_image = random.choice(images)
    return render(request, 'quote.html', {'quote': selected_quote, 'image': selected_image})

def show_all(request):
    return render(request, 'show_all.html', {'quotes': quotes, 'images': images})

def about(request):
    person_info = "Famous Person: Nelson Mandela"
    creator_info = "Created by: Kanghuan Xu"
    return render(request, 'about.html', {'person_info': person_info, 'creator_info': creator_info})
