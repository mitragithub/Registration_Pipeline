import numpy
import glob

def readrigid(brainno,sliceno):
	rtfile = glob.glob('%s/%s_AAV_registered_rigidtrans/*_%.4d_rigidtrans.txt' % (brainno,brainno,int(sliceno)))
	dat = numpy.loadtxt(rtfile)
	Rt = dat.reshape(3,2)
	R = Rt[:2,:]
	T = Rt[2,:]
	return (R,T)

if __name__=="__main__":
	R,T=readrigid('PMD1080',131)
	print R
	print T

