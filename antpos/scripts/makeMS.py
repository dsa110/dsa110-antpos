import numpy as np, os


# IO
ofile = 'psf.ms' # output MS
os.system('rm -rf '+ofile)
antlist = 'antlist_case2.npz' # choose antlist made by make_antlist.py

# define common DSA-110 parameters 

# antennas
tname = 'OVRO_MMA'
diam = 4.65 # m
obs = 'OVRO_MMA'
mount = 'alt-az'
pos_obs = me.observatory(obs)

# get antlist
f = np.load(antlist)
xx = f['xx']
yy = f['yy']
zz = f['zz']

# backend
spwname = 'L_BAND'
freq = '1.53GHz'
deltafreq = '-0.244140625MHz'
freqresolution = deltafreq
nchannels = 1024
integrationtime = '0.001s'
stoptime = '0.001s'

# source/observation characteristics
sourcename = 'SNAPSHOT'
obstm = 58000.0 # mjd
epoch = me.epoch('utc',qa.quantity(obstm,'d'))
d = me.direction('HADEC','0.0deg','22.0deg')
me.doframe(epoch)
me.doframe(pos_obs)
me.doframe(d)
# these are on the meridian
ra = me.measure(d,'RADEC')['m0']['value'] # rad
dec = me.measure(d,'RADEC')['m1']['value'] # rad
print('RA',ra,'DEC',dec)

# make new ms

sm.open(ofile)

sm.setconfig(telescopename=tname, x=xx, y=yy, z=zz, dishdiameter=diam, mount=mount, antname=tname, coordsystem='global', referencelocation=pos_obs)

sm.setspwindow(spwname=spwname, freq=freq, deltafreq=deltafreq, freqresolution=freqresolution, nchannels=nchannels, stokes='I')

sm.settimes(integrationtime=integrationtime, usehourangle=False, referencetime=epoch)

sm.setfield(sourcename=sourcename, sourcedirection=me.direction('J2000',qa.quantity(ra,'rad'),qa.quantity(dec,'rad')))

sm.setauto(autocorrwt=0.0)

# observe it

sm.observe(sourcename, spwname, starttime='0s', stoptime=stoptime)

# close

sm.close()

# get rid of flags

flagdata(vis=ofile,mode='unflag')

# put data at phase center

det_snr = 10.0
bf_eff = 0.9

bl_snr_chan = (det_snr/bf_eff)*np.sqrt(2.)/20./np.sqrt(1.*nchannels)

ms.open(ofile,nomodify=False)
ms.selectinit(datadescid=0)
rec = ms.getdata(["data"]) # rec['data'] has shape [scan, channel, [time*baseline]]
# vis has shape [channel,baseline]
vis = bl_snr_chan + np.random.normal(size=rec['data'][0,:,:].shape) + np.random.normal(size=rec['data'][0,:,:].shape)*1j
rec['data'][0,:,:] = vis
ms.putdata(rec)

# make image

im.open(ofile)
im.selectvis(uvrange='>20')
im.defineimage(nx=2048,ny=2048,cellx='2arcsec',celly='2arcsec',stokes='I',mode='mfs')
im.weight('natural')
im.setoptions(gridfunction='BOX')

im.makeimage(type='observed',image='test')

ia.open('test')
ia.tofits('test.fits',overwrite=True)
ia.close()

# clean and fit
tclean(vis='psf.ms',imagename='test',imsize=2048,cell='2arcsec',specmode='mfs',niter=10,cycleniter=10,weighting='natural',datacolumn='data',uvrange='>30',deconvolver='hogbom')
imfit(imagename='test.image',box='980,980,1068,1068')
ia.open('test.image')
ia.tofits('test_clean.fits',overwrite=True)
ia.close()
