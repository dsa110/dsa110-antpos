import pandas
import antpos
from astropy.coordinates import EarthLocation
import astropy.units as u
import numpy as np

from pkg_resources import resource_filename
#antposfile = resource_filename("antpos", "data/DSA110_positions_RevF.csv")  # early 2020 versions
antposfile = resource_filename("antpos", "data/DSA110_Station_Coordinates.csv")  # sep 2020 version
antidfile = resource_filename("antpos", "data/ant_ids.csv")

def __init__():
    return

def tee_centers(csvfile=antposfile):
    """ Read positions of DSA110 Tee center and return as tuple.
    """

#    tab0         = pandas.read_csv(csvfile)   # early 2020 versions
#    tc_latitude  = float(tab0.iloc[4][3])
#    tc_longitude = float(tab0.iloc[5][3])
    tab0         = pandas.read_csv(csvfile, skiprows=6)  # sep 2020 version
    tc_latitude = tab0.iloc[3,2]
    tc_longitude = tab0.iloc[3,3]

    return (tc_latitude, tc_longitude)

def get_lonlat(csvfile=antposfile, headerline=5):
    """ Read positions of all antennas from DSA110 CSV file.
    """

    tab       = pandas.read_csv(csvfile, header=headerline)
#    stations  = pandas.concat([tab['Station Number'], tab['Station Number.1']])
#    latitude  = pandas.concat([tab['Latitude'], tab['Latitude.1']])
#    longitude = pandas.concat([tab['Longitude'], tab['Longitude.1']])
    stations  = tab['Station Number']
    latitude  = tab['Latitude']
    longitude = tab['Longitude']

    df = pandas.DataFrame()
    df['Station Number'] = [int(station.split('-')[1]) for station in stations]
    df['Latitude'] = latitude
    df['Longitude'] = longitude
    for st_no in ['200E', '200W']:
        idx_to_drop = np.where(df['Station Number'] == st_no)[0]
        if len(idx_to_drop > 0):
            df.drop(idx_to_drop[0], inplace=True)
    df = df.astype({'Station Number': np.int32})
    df.sort_values(by=['Station Number'], inplace=True)
    df.set_index('Station Number', inplace=True)
    return df

def get_itrf(csvfile=antposfile, height=None, latlon_center=None,
             return_all_stations=True, stations=antidfile):
    """Read positions of all antennas from DSA110 CSV file and 
    convert to ITRF coordinates. Only provides active stations."""

    if height is None:
        height = 1222*u.m
    if latlon_center is None:
        (latcenter, loncenter) = tee_centers()
    else:
        (latcenter, loncenter) = latlon_center

    df = get_lonlat(csvfile)
    center = EarthLocation(lat=latcenter, lon=loncenter, height=height)
    df['x_m'] = EarthLocation(lat=df['Latitude'], lon=df['Longitude'], height=height).x.to_value(u.m)
    df['y_m'] = EarthLocation(lat=df['Latitude'], lon=df['Longitude'], height=height).y.to_value(u.m)
    df['z_m'] = EarthLocation(lat=df['Latitude'], lon=df['Longitude'], height=height).z.to_value(u.m)

    df['dx_m'] = (EarthLocation(lat=df['Latitude'], lon=df['Longitude'], height=height).x-center.x).to_value(u.m)
    df['dy_m'] = (EarthLocation(lat=df['Latitude'], lon=df['Longitude'], height=height).y-center.y).to_value(u.m)
    df['dz_m'] = (EarthLocation(lat=df['Latitude'], lon=df['Longitude'], height=height).z-center.z).to_value(u.m)

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
    df_bls = pandas.DataFrame(columns=['bname','x_m','y_m','z_m'])
    for i in np.arange(1 if not autocorrs else 0, nant):
        for j in np.arange(i if not autocorrs else i+1):
            a1 = antenna_order[i]
            a2 = antenna_order[j]
            df_bls = df_bls.append(
                {'bname':'{0}-{1}'.format(a1,a2),
                 'x_m':df.loc[a1]['x_m']-df.loc[a2]['x_m'],
                 'y_m':df.loc[a1]['y_m']-df.loc[a2]['y_m'],
                 'z_m':df.loc[a1]['z_m']-df.loc[a2]['z_m']},
                 ignore_index=True)
    if casa_order:
        df_bls = df_bls.iloc[::-1]
        df_bls.reset_index(inplace=True, drop=True)
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

