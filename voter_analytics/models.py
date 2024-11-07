from django.db import models
import csv
from django.conf import settings
from django.utils.dateparse import parse_date
from pathlib import Path

# Create your models here.
from django.db import models

class Voter(models.Model):
    voter_id = models.CharField(max_length=50, unique=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=10, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=50)
    precinct_number = models.CharField(max_length=2)
    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)
    
    voter_score = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.voter_id})"
    


def load_data(csv_path='newton_voters.csv'):
    csv_file_path = Path(settings.BASE_DIR) / csv_path

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        voter_objects = []
        
        for row in reader:
            voter = Voter(
                voter_id=row['Voter ID Number'],
                last_name=row['Last Name'],
                first_name=row['First Name'],
                street_number=row['Residential Address - Street Number'],
                street_name=row['Residential Address - Street Name'],
                apartment_number=row.get('Residential Address - Apartment Number', None),
                zip_code=row['Residential Address - Zip Code'],
                date_of_birth=parse_date(row['Date of Birth']),
                date_of_registration=parse_date(row['Date of Registration']),
                party_affiliation=row['Party Affiliation'],
                precinct_number=row['Precinct Number'],
                v20state=(row['v20state'] == "TRUE"),
                v21town=(row['v21town'] == "TRUE"),
                v21primary=(row['v21primary'] == "TRUE"),
                v22general=row['v22general'] == "TRUE",
                v23town=row['v23town'] == "TRUE",
                voter_score=int(row['voter_score'])
            )
            voter_objects.append(voter)
        
        Voter.objects.bulk_create(voter_objects)
