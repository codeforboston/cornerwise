#from django.test import TestCase
from hypothesis.extra.django.models import models
from proposal.models import Proposal

from hypothesis import given
from hypothesis import strategies
from hypothesis.strategies import composite, fixed_dictionaries, integers, just, sampled_from, text


@composite
def addresses(draw):
    num = draw(integers(min_value=1, max_value=1000))
    name = draw(text())
    st_type = draw(sampled_from(["St", "Rd", ""]))

    return "{} {} {}".format(num, name, st_type)

@composite
def case_number(draw):
    authority = draw(sampled_from(["PB", "ZBA"]))
    year = draw(integers(min_value=2014, max_value=2020))
    n = draw(integers())

    return "{authority} {year}-{n}".format()



regions_strategy = sampled_from(["Somerville, MA", "Cambridge, MA"])

proposal_strategy = fixed_dictionaries({
    "address": addresses,
    "region_name": regions_strategy
})

@given(proposal_strategy)
def generate_proposal(p):
    pass

