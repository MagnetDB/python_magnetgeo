import yaml
from python_magnetgeo.InnerCurrentLead import InnerCurrentLead
from python_magnetgeo.OuterCurrentLead import OuterCurrentLead

import json


def test_innercurrentlead():
    ofile = open("Inner.yaml", "w")
    r = [38.6 / 2.0, 48.4 / 2.0]
    h = 480.0
    bars = [123, 12, 90, 60, 45, 3]
    support = [24.2, 0]
    yaml.dump(InnerCurrentLead("Inner", r, 480.0, bars, support, False), ofile)


def test_outercurrentlead():
    ofile = open("Outer.yaml", "w")
    r = [172.4, 186]
    h = 10.0
    bars = [10, 18, 15, 499]
    support = [48.2, 10, 18, 45]
    yaml.dump(OuterCurrentLead("Outer", r, h, bars, support), ofile)


def test_loadlead():
    lead = yaml.load(open("Inner.yaml", "r"), Loader=yaml.FullLoader)
    assert lead.r[0] == 19.3


def test_jsonlead():
    lead = yaml.load(open("Inner.yaml", "r"), Loader=yaml.FullLoader)
    lead.write_to_json()

    # load from json
    jsondata = lead.read_from_json()
    assert jsondata.name == "Inner" and jsondata.r[0] == 19.3
