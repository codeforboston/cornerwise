from django.conf import settings
from django.test import TestCase

from datetime import datetime, timedelta
from pprint import pprint

from proposal.models import Event, Importer, Proposal
from scripts import gmaps
from utils import add_locations


proposal_dict = {'all_addresses': ['21 Cherry Street'],
                 'case_number': 'ZBA 2017-123',
                 'complete': True,
                 'decisions': {'links': [{'title': 'Decision',
                                          'url': 'https://www.somervillema.gov/sites/default/files/CherrySt21.pdf'}]},
                 'events': [{'description': 'The ZBA is the Special Permit Granting Authority '
                             'for variances; appeals of decisions; '
                             'Comprehensive Permit Petitions; and some Special '
                             'Permit applications',
                             'region_name': 'Somerville, MA',
                             'start': '2017-05-17T18:00:00',
                             'title': 'Zoning Board of Appeals'}],
                 'first_hearing_date': '2017-05-17T00:00:00',
                 'number': '21',
                 'other': {'links': [{'title': 'Final Plan Set',
                                      'url': 'https://www.somervillema.gov/sites/default/files/Cherry%20St%2021%20-%20Final%20Combined%20Plan%20Sets%20for%20May%2017%202017%20ZBA%20hearing_0.pdf'}]},
                 'reports': {'links': [{'title': 'Staff Report',
                                        'url': 'https://www.somervillema.gov/sites/default/files/Cherry%20St%2021%20-%20Updated%20Staff%20Report%20May%202017-FINAL.pdf'}]},
                 'source': 'https://www.somervillema.gov/departments/ospcd/planning-and-zoning/reports-and-decisions/robots',
                 'street': 'Cherry Street',
                 'updated_date': '2017-10-02T11:49:00-04:00',
                 "attributes": [
                     ("Applicant Name", "Sally Bobson")
                 ]}


class TestImport(TestCase):
    def setUp(self):
        self.region = "Somerville, MA"
        self.addresses = ["240 Elm Street", "100 Broadway", "115 Medford Street"]
        self.geocoder = gmaps.GoogleGeocoder(settings.GOOGLE_API_KEY)
        self.proposal_importer_url = "https://58kr1azj04.execute-api.us-east-1.amazonaws.com/prod/somervillema"

    def test_add_locations(self):
        dicts = [
            {"all_addresses": [addr]} for addr in self.addresses
        ]
        add_locations(dicts, self.geocoder)
        for addressed in dicts:
            self.assertTrue("location" in addressed)
            self.assertIsInstance(addressed["location"]["lat"], float)
            self.assertIsInstance(addressed["location"]["long"], float)

    def test_create_from_dict(self):
        # TODO: Generate a valid input dict rather than use static dict
        pdict = proposal_dict.copy()
        with self.assertRaises(Exception):
            Proposal.create_or_update_from_dict(pdict)
        add_locations([pdict], self.geocoder)

        # Delete any existing proposals for this case:
        Proposal.objects.filter(case_number=pdict["case_number"]).delete()
        (created, proposal) = Proposal.create_or_update_from_dict(pdict)

        self.assertTrue(created)
        self.assertEqual(proposal.document_set.count(),
                         len(pdict["decisions"]) +
                         len(pdict["other"]) +
                         len(pdict["reports"]))

    def test_importer(self):
        importer = Importer(name="My Importer",
                            url=self.proposal_importer_url)
        cases = importer.cases_since(datetime.now() - timedelta(days=30))
        add_locations(cases[0:1], self.geocoder)
        (created, proposal) = Proposal.create_or_update_from_dict(cases[0])
        self.assertTrue(created)
        self.assertIsInstance(proposal, Proposal)

    def test_changes(self):
        pdict = proposal_dict.copy()
        add_locations([pdict], self.geocoder)

        # Ensure that the proposal is already created:
        Proposal.create_or_update_from_dict(pdict)

        # new attribute:
        pdict["attributes"].append(("Owner Name", "Empire Holdings, LLC"))
        # changed attribute:
        pdict["attributes"].append(("Applicant Name", "Darth Vader"))
        # changed property:
        pdict["description"] = ("Proposal to build a space elevator on previous "
                                "location of Mom and Pop hardware store")

        (created, proposal) = Proposal.create_or_update_from_dict(pdict)
        self.assertFalse(created)
        changesets = proposal.changesets.all()

        self.assertEqual(len(changesets), 1)
        changes = changesets[0].changes

        for change in changes["attributes"] + changes["properties"]:
            # It should not record something as a change if it has not, in fact
            # changed:
            self.assertNotEqual(change["old"], change["new"])

        changed_attribute_names = [c["name"] for c in changes["attributes"]]
        changed_property_names = [c["name"] for c in changes["properties"]]
        self.assertIn("Owner Name", changed_attribute_names)
        self.assertIn("Applicant Name", changed_attribute_names)
        self.assertIn("description", changed_property_names)


    def test_something(self):
        pass

    def tearDown(self):
        pass
        # Proposal.objects.all().delete()
