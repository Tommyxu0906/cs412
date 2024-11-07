from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter
from django.db.models import Q
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Count

# Create your views here.

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        queryset = Voter.objects.all()
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
        context['voter_scores'] = range(6) 
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        return context


class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'


class GraphsView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_queryset(self):
        queryset = Voter.objects.all()
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
        
        birth_years = self.get_queryset().values_list('date_of_birth', flat=True)
        birth_years = [dob.year for dob in birth_years if dob]
        birth_year_counts = {year: birth_years.count(year) for year in set(birth_years)}
        birth_year_histogram = px.bar(
            x=list(birth_year_counts.keys()),
            y=list(birth_year_counts.values()),
            labels={'x': 'Year of Birth', 'y': 'Count'},
            title=f"Voter distribution by Year of Birth (n={len(birth_years)})"
        )
        birth_year_histogram_div = birth_year_histogram.to_html(full_html=False)

        party_counts = self.get_queryset().values('party_affiliation').annotate(count=Count('party_affiliation'))
        party_pie = px.pie(
            values=[p['count'] for p in party_counts],
            names=[p['party_affiliation'] for p in party_counts],
            title=f"Voter distribution by Party Affiliation (n={len(self.get_queryset())})",
        )
        party_pie_div = party_pie.to_html(full_html=False)

        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        election_counts = []
        for election in elections:
            count = self.get_queryset().filter(**{election: True}).count()
            election_counts.append(count)

        election_histogram = px.bar(
            x=elections,
            y=election_counts,
            labels={'x': 'Election', 'y': 'Vote Count'},
            title=f"Vote Count by Election (n={len(self.get_queryset())})"
        )
        election_histogram_div = election_histogram.to_html(full_html=False)

        context['birth_year_histogram'] = birth_year_histogram_div
        context['party_pie'] = party_pie_div
        context['election_histogram'] = election_histogram_div
        context['party_affiliations'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        context['years'] = range(1900, date.today().year + 1)
        context['voter_scores'] = range(6) 
        context['elections'] = elections
        return context
