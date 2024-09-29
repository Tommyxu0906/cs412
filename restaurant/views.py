from django.shortcuts import render

# Create your views here.
import random
import time
from django.utils import timezone
from datetime import datetime

def main(request):
    context = {
        'image': '/static/images/store.jpg',  # Adjust the path as needed
        'current_time': datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    }
    return render(request, 'restaurant/main.html', context)


# View for the order page
def order(request):
    return render(request, 'restaurant/order.html')

import random
from datetime import datetime, timedelta

def confirmation(request):
    if request.method == 'POST':
        # Retrieve the checked items
        fried_chicken = []
        if request.POST.get('10boneless'):
            fried_chicken.append('10 Boneless')
        if request.POST.get('10wings'):
            fried_chicken.append('10 Wings')
        if request.POST.get('20boneless'):
            fried_chicken.append('20 Boneless')
        if request.POST.get('20wings'):
            fried_chicken.append('20 Wings')

        special = request.POST.get('kfood', 'No special')

        # Special instructions
        special_instructions = request.POST.get('special_instructions', 'No instructions')

        # Customer info
        customer_name = request.POST.get('name')
        customer_phone = request.POST.get('phone')
        customer_email = request.POST.get('email')

        # Calculate total price
        prices = {
            '10 Boneless': 10,
            '10 Wings': 10,
            '20 Boneless': 20,
            '20 Wings': 20,
            'Fried Rice': 10
        }
        total = sum(prices.get(item, 0) for item in fried_chicken)
        if special == 'Fried Rice':
            total += 10

        # Randomly add 30-60 minutes to the current time for ready time
        random_minutes = random.randint(30, 60)
        ready_time = datetime.now() + timedelta(minutes=random_minutes)
        ready_time_str = ready_time.strftime("%a %b %d %H:%M:%S %Y")

        # Current time (for generation timestamp)
        generated_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")

        # Context to pass to the template
        context = {
            'fried_chicken': fried_chicken,
            'special': special,
            'special_instructions': special_instructions,
            'total': total,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            'ready_time': ready_time_str,
            'generated_time': generated_time
        }

        return render(request, 'restaurant/confirmation.html', context)

    return redirect('order')  # Redirect back to order page if no POST data
