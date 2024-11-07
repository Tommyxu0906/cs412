from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Voter
from django.db.models import Q
from datetime import date


# Create your views here.

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        queryset = Voter.objects.all()
        # Filtering logic here remains the same as previous code
        party_affiliation = self.request.GET.get('party_affiliation')
        if party_affiliation:
            queryset = queryset.filter(party_affiliation=party_affiliation)
        
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        if min_dob:
            queryset = queryset.filter(date_of_birth__gte=date(int(min_dob), 1, 1))
        if max_dob:
            queryset = queryset.filter(date_of_birth__lte=date(int(max_dob), 12, 31))

        voter_score = self.request.GET.get('voter_score')
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))

        for election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if self.request.GET.get(election):
                queryset = queryset.filter(**{election: True})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['party_affiliations'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        context['years'] = range(1900, date.today().year + 1)
        context['voter_scores'] = range(6)  # Assuming voter_score ranges from 0 to 5
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']  # Pass the list of elections here
        return context


# voter_analytics/views.py
class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'
