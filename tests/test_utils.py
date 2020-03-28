from antpos import utils

from pkg_resources import Requirement, resource_filename
antposfile = resource_filename(Requirement.parse("dsa110-antpos"), "antpos/data/DSA110_positions_RevD.csv")

def test_get():
    df = utils.get_itrf(csvfile=antposfile)

def test_frb():
    days = utils.get_days_per_frb(nant=100,beam_correct=False)


