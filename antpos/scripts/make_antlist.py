import numpy as np
from antpos import utils

# antenna positions
df = utils.get_itrf(stations='../data/ant_ids_case2.csv')
xx = np.asarray(df['x_m'].array)
yy = np.asarray(df['y_m'].array)
zz = np.asarray(df['z_m'].array)

np.savez('antlist_case2.npz',xx=xx,yy=yy,zz=zz)

