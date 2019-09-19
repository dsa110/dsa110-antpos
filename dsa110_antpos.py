import pandas

def tee_centers(csvfile = 'DSA110_positions_RevD.csv'):
    """ Read positions of DSA110 Tee center and return as tuple.
    """

    tab0 = pandas.read_csv(csvfile)
    tc_latitude = float(tab0.iloc[4][3])
    tc_longitude = float(tab0.iloc[5][3])

    return (tc_latitude, tc_longitude)

def antpos(csvfile = 'DSA110_positions_RevD.csv', headerline=13):
    """ Read positions of all antennas from DSA110 CSV file.
    """

    tab = pandas.read_csv(csvfile, header=headerline)
    stations = pandas.concat([tab['Station Number'], tab['Station Number.1']])
    latitude = pandas.concat([tab['Latitude'], tab['Latitude.1']])
    longitude = pandas.concat([tab['Longitude'], tab['Longitude.1']])

    return pandas.concat((stations, latitude, longitude), axis=1) 
