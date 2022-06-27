import pandas
from collections import namedtuple
import antpos
from astropy.coordinates import EarthLocation
import astropy.units as u
import numpy as np

from pkg_resources import resource_filename
antposfile = resource_filename("antpos", "data/DSA110_Station_Coordinates.csv")
antidfile = resource_filename("antpos", "data/ant_ids.csv")

def __init__():
    return

def tee_centers():
    """ Read positions of DSA110 Tee center and return as tuple.
    """
    tc_longitude = -2.064427799136453*u.rad
    tc_latitude = 0.6498455107238486*u.rad
    tc_height = 1188.0519*u.m

    return (tc_latitude, tc_longitude, tc_height)

def get_lonlat(csvfile=antposfile, headerline=5, defaultheight=1182.6000):
    """ Read positions of all antennas from DSA110 CSV file.
    """

    tab       = pandas.read_csv(csvfile, header=headerline)
    stations  = tab['Station Number']
    latitude  = tab['Latitude']
    longitude = tab['Longitude']
    height = tab['Elevation (meters)']

    df = pandas.DataFrame()
    df['Station Number'] = [int(station.split('-')[1]) for station in stations]
    df['Latitude'] = latitude
    df['Longitude'] = longitude
    df['Height (m)'] = height
    df['Height (m)'] = np.where(np.isnan(df['Height (m)']), defaultheight, df['Height (m)'])
    for st_no in ['200E', '200W']:
        idx_to_drop = np.where(df['Station Number'] == st_no)[0]
        if len(idx_to_drop > 0):
            df.drop(idx_to_drop[0], inplace=True)
    df = df.astype({'Station Number': np.int32})
    df.sort_values(by=['Station Number'], inplace=True)
    df.set_index('Station Number', inplace=True)
    return df

def get_itrf(csvfile=antposfile, latlon_center=None,
             return_all_stations=True, stations=antidfile):
    """Read positions of all antennas from DSA110 CSV file and 
    convert to ITRF coordinates. Only provides active stations."""

    if latlon_center is None:
        (latcenter, loncenter, heightcenter) = tee_centers()
    else:
        (latcenter, loncenter, heightcenter) = latlon_center

    df = get_lonlat(csvfile)
    center = EarthLocation(lat=latcenter, lon=loncenter, height=heightcenter)
    locations = EarthLocation(lat=df['Latitude'], lon=df['Longitude'], height=df['Height (m)']*u.m)
    df['x_m'] = locations.x.to_value(u.m)
    df['y_m'] = locations.y.to_value(u.m)
    df['z_m'] = locations.z.to_value(u.m)

    df['dx_m'] = (locations.x-center.x).to_value(u.m)
    df['dy_m'] = (locations.y-center.y).to_value(u.m)
    df['dz_m'] = (locations.z-center.z).to_value(u.m)

    if not return_all_stations:
        idxs = np.genfromtxt(stations, dtype=np.int, delimiter=',')
        df = df.loc[idxs]

    return df

def get_baselines(antenna_order, casa_order=True, autocorrs=False):
    # Antenna order is the order of the antennas in the correlator
    # CASA orders the baselines in the reverse direction as the correlator
    # If casa_order is True, the baseline order will be swapped in order to
    # match casa standards.  Else, the order will be left to match the output
    # from the correlator.
    nant = len(antenna_order)
    df = get_itrf()
    df_bls = []
    baseline = namedtuple('baseline', 'bname x_m y_m z_m')
    for i in np.arange(1 if not autocorrs else 0, nant):
        for j in np.arange(i if not autocorrs else i+1):
            a1 = antenna_order[j]
            a2 = antenna_order[i]
            df_bls.append(
                baseline(
                    '{0}-{1}'.format(int(a1), int(a2)),
                    df.loc[a2]['x_m']-df.loc[a1]['x_m'],
                    df.loc[a2]['y_m']-df.loc[a1]['y_m'],
                    df.loc[a2]['z_m']-df.loc[a1]['z_m'],
            ))
    if casa_order:
        df_bls = df_bls[::-1]
    
    df_bls = pandas.DataFrame.from_records(df_bls, columns=['bname','x_m','y_m','z_m'])

    return df_bls
                                          
def get_days_per_frb(nant=20,srch_efficiency=0.9,threshold=10.0,beam_correct=True):
    """Implements James+19 and Bhandari+18 FRB fluence distribution
    to derive the days per FRB detection for different nant. All 
    efficiencies (bf, srch code, etc) are folded into the 
    srch_efficiency parameter. Hardcoded for DSA-110 using latest 
    SEFD estimate. beam_correct lowers sensitivity by x2."""

    sefd = 6500.0/(1.*nant) # Jy
    bw = 200.0 # MHz    
    fluence_thresh = threshold*(sefd/srch_efficiency)/np.sqrt(2.*0.001*bw*1e6)

    if beam_correct:
        fluence_thresh *= 2.
    
    Fb = 15. # Jy ms
    F0 = 2. # Jy ms
    R0 = 1700 # per sky per day above F0
    a1 = -1.2
    a2 = -2.2
    Rb = R0*(Fb/F0)**(a1)

    fov_sky = 11./41253.
    
    if fluence_thresh>=Fb:
        return 1./(fov_sky*Rb*(fluence_thresh/Fb)**(a2))
    return 1./(fov_sky*R0*(fluence_thresh/F0)**(a1))

