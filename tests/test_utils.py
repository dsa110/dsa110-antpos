import random
import astropy.units as u
from antpos import utils
import antpos
from pkg_resources import Requirement, resource_filename

#antposfile = resource_filename(Requirement.parse("dsa110-antpos"), "dsa110-antpos/antpos/data/DSA110_Station_Coordinates.csv")
antposfile = antpos.__path__[0] + "/data/DSA110_Station_Coordinates.csv"

def test_get():
    df = utils.get_itrf(csvfile=antposfile)

def test_frb():
    days = utils.get_days_per_frb(nant=100,beam_correct=False)

def test_get_itrf():
    df = utils.get_itrf()
    ovro_lon = -118.283400*u.deg
    ovro_lat = 37.233386*u.deg
    ovro_height = 1188*u.m
    df = utils.get_itrf(height=ovro_height, latlon_center=(ovro_lat, ovro_lon))

def test_get_baselines():
    df = utils.get_lonlat()
    nant = 10
    antenna_order = [df.index[i] for i in random.sample(range(len(df.index)), nant)]
    print(antenna_order)
    df_bls = utils.get_baselines(antenna_order, autocorrs=True, casa_order=False)
    assert len(df_bls['bname']) == (nant*(nant+1))//2
    assert df_bls['bname'][0] == '{0}-{0}'.format(antenna_order[0])
    assert len(df_bls['bname']) == len(df_bls['x_m'])
    assert len(df_bls['bname']) == len(df_bls['y_m'])
    assert len(df_bls['bname']) == len(df_bls['z_m'])
    df_bls = utils.get_baselines(antenna_order, autocorrs=False, casa_order=False)
    assert len(df_bls['bname']) == (nant*(nant-1))//2
    assert df_bls['bname'][0] == '{0}-{1}'.format(antenna_order[0],
                                                   antenna_order[1])
    df_bls = utils.get_baselines(antenna_order, casa_order=True)
    print(antenna_order)
    print(df_bls['bname'][(nant*(nant-1))//2-1])
    assert df_bls['bname'][(nant*(nant-1))//2-1] == '{0}-{1}'.format(antenna_order[0],
                                                   antenna_order[1])
