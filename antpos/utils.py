import pandas
import antpos
from astropy.coordinates import EarthLocation
import astropy.units as u
import numpy as np

def __init__():
    return

def tee_centers(csvfile='{0}/data/DSA110_positions_RevD.csv'.format(antpos.__path__[0])):
    """ Read positions of DSA110 Tee center and return as tuple.
    """

    tab0         = pandas.read_csv(csvfile)
    tc_latitude  = float(tab0.iloc[4][3])
    tc_longitude = float(tab0.iloc[5][3])

    return (tc_latitude, tc_longitude)

def get_lonlat(csvfile='{0}/data/DSA110_positions_RevD.csv'.format(antpos.__path__[0]), headerline=13):
    """ Read positions of all antennas from DSA110 CSV file.
    """

    tab       = pandas.read_csv(csvfile, header=headerline)
    stations  = pandas.concat([tab['Station Number'], tab['Station Number.1']])
    latitude  = pandas.concat([tab['Latitude'], tab['Latitude.1']])
    longitude = pandas.concat([tab['Longitude'], tab['Longitude.1']])

    df = pandas.DataFrame()
    df['Station Number'] = stations
    df['Latitude'] = latitude
    df['Longitude'] = longitude
    df.set_index('Station Number', inplace=True)
    
    return df

def get_itrf(csvfile='{0}/data/DSA110_positions_RevD.csv'.format(antpos.__path__[0]),
             headerline=13,height=1222*u.m):
    """Read positions of all antennas from DSA110 CSV file and 
    convert to ITRF coordinates."""

    df = get_lonlat(csvfile,headerline)
    (latcenter,loncenter) = tee_centers()
    center = EarthLocation(lat=latcenter,lon=loncenter,height=height)
    df['x_m'] = EarthLocation(lat=df['Latitude'],lon=df['Longitude'],height=height).x.to_value(u.m)
    df['y_m'] = EarthLocation(lat=df['Latitude'],lon=df['Longitude'],height=height).y.to_value(u.m)
    df['z_m'] = EarthLocation(lat=df['Latitude'],lon=df['Longitude'],height=height).z.to_value(u.m)

    df['dx_m'] = (EarthLocation(lat=df['Latitude'],lon=df['Longitude'],height=height).x - center.x).to_value(u.m)
    df['dy_m'] = (EarthLocation(lat=df['Latitude'],lon=df['Longitude'],height=height).y - center.y).to_value(u.m)
    df['dz_m'] = (EarthLocation(lat=df['Latitude'],lon=df['Longitude'],height=height).z - center.z).to_value(u.m)

    return df

def get_baselines(antenna_order,casa_order=True,autocorrs=False):
    # Antenna order is the order of the antennas in the correlator
    # CASA orders the baselines in the reverse direction as the correlator
    # If casa_order is True, the baseline order will be swapped in order to
    # match casa standards.  Else, the order will be left to match the output
    # from the correlator.
    nant = len(antenna_order)
    df = get_itrf()
    df_bls = pandas.DataFrame(columns=['bname','x_m','y_m','z_m'])
    for i in np.arange(1 if not autocorrs else 0,nant):
        for j in np.arange(i if not autocorrs else i+1):
            a1 = antenna_order[i]
            a2 = antenna_order[j]
            
            df_bls = df_bls.append({'bname':'{0}-{1}'.format(a1,a2),
                           'x_m':df.loc[a1]['x_m']-df.loc[a2]['x_m'],
                           'y_m':df.loc[a1]['y_m']-df.loc[a2]['y_m'],
                                   'z_m':df.loc[a1]['z_m']-df.loc[a2]['z_m']},
                          ignore_index=True)
    if casa_order:
        df_bls = df_bls.iloc[::-1]
        df_bls.reset_index(inplace=True,drop=True)
    return df_bls
                                          
