import numpy as np
import math
import scipy.linalg as linalg

class SimClass(object):
	"""
	Simulation class. Contains all variables and needed parameters 
	to solve Laplace's equation on a domain.
	"""
	def __init__(self,data=''):
		self.data = data
		self.readInput()

	def readInput(self):
		"""
		Read input data and assign parameters
		"""
		if self.data == '': #If no input data is defined
			self.data = [2,1,'circle',2,2,3+3j,-2.5-2.5j, 'superlow']
	
		self.nbr_panels = self.data[0] #nbr interface points
		self.nbr_dom = self.data[1] #nbr domain points
		self.shape = self.data[2] #shape of interface
		self.radius = self.data[3]
		nbr_src = self.data[4] #nbr sources for RHS
		self.src = [] #sources for RHS
		for i in range(nbr_src):
			x = self.data[5+i]
			self.src.append(x)
		self.fillLevel = (self.data[-1])

	def setUp(self):
		"""
		Set up simulation.
		"""
		self.createInterface()
		self.fillDomain()
		self.RHS = self.rhsf()

	def rhsf(self,x=-100):
		"""
		Compute RHS given by sources.
		"""
		if np.size(x) == 1: 
			if x == -100:
				x = self.zDrops
				f = np.zeros(np.shape(x))
				for j in range(np.size(f)):
					for i in range(len(self.src)):
						f[j] += np.real(1/(x[j]-self.src[i]))
			else:
				f = 0
				for i in range(len(self.src)):
						f += np.real(1/(x-self.src[i]))
		else:
			f = np.zeros(np.shape(x))
			for j in range(np.size(f)):
				for i in range(len(self.src)):
					f[j] += np.real(1/(x[j]-self.src[i]))
		return f

	def fillDomain(self):
		"""
		Fill domain (interior) with computational points for evaluating solution.
		"""
		if self.fillLevel == "superlow":
			nbrR = 10
			nbrT = 10
		else:
			if self.fillLevel == "low":
				nbrR = 20
				nbrT = 20
		R1 = 0.4 #where to go from sparse to dense disc. in domain
		r1 = np.linspace(0,R1,5)
		r2 = np.linspace(R1,0.999,nbrR); 
		r2 = r2[1:]
		r = np.append(r1, r2) #radial discretisation
		t = np.linspace(0,2*math.pi,nbrT+1); t = t[0:-1]
		R,T = np.meshgrid(r,t)

		self.zDom = np.zeros((np.size(t),np.size(r)))
		zD = self.zDom
		zD = zD.reshape(np.size(zD))
		RD = R.reshape(np.size(R))
		TD = T.reshape(np.size(T))

		zD = RD*(self.radius*np.cos(TD) + self.radius*1j*np.sin(TD))
		self.zDom = zD.reshape(np.shape(self.zDom))

	def createInterface(self):
		"""
		Create interface discretization.
		"""
		# Create panels
		self.tpanels = np.linspace(0,2*math.pi,self.nbr_panels+1)
		self.zpanels = self.radius*np.cos(self.tpanels) + self.radius*1j*np.sin(self.tpanels)

		# Create empty arrays for interface points and weights
		self.tDrops = np.zeros(self.nbr_panels*16)
		self.wDrops = np.zeros(self.nbr_panels*16)
		for i in range(self.nbr_panels): #Go through all panels!
			n,w = self.gaussLeg(16,self.tpanels[i],self.tpanels[i+1])
			self.tDrops[i*16:(i+1)*16] = n
			self.wDrops[i*16:(i+1)*16] = w
		self.zDrops = (self.radius*np.cos(self.tDrops) + 
			self.radius*1j*np.sin(self.tDrops))
		self.zpDrops = (-self.radius*np.sin(self.tDrops) +
			self.radius*1j*np.cos(self.tDrops))
		self.zppDrops = -self.zDrops

	def gaussLeg(self,n,t1,t2):
		"""
		Create Gauss-Legendre nodes and weights of order n, on interval [t1,t2]. 
		As done in Trefethen.
		"""
		n_vec = np.linspace(1,15,15)
		beta = 0.5*(1-(2*n_vec)**(-2))**(-1/2)
		T = np.diag(beta,-1) + np.diag(beta,1)
		D,V = linalg.eig(T)
		nodes = np.real((t1*(1-D)+t2*(1+D))/2) #Remap to [t1,t2]
		weights = 2*(V[0]**2).T
		weights = (t2-t1)/2*weights
		idx = np.argsort(nodes)
		nodes = np.array(nodes)[idx]
		weights = np.array(weights)[idx]
		return nodes, weights

if __name__ == "__main__":
	print('Simulation class')
	sc = SimClass()
	sc.setUp()

