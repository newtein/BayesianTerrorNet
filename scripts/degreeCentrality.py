
# coding: utf-8

# In[35]:


from collections import OrderedDict
import pickle

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import networkx as nx
from mpl_toolkits.basemap import Basemap


# In[32]:


def getGeoCoding(name):
	g = geocoder.google(name)
	return g.latlng

def getCountryGeo(locations,name):
	if name in ["''","'.'",0]:
		return locations
	else:
		
		if locations.get(name,''):
			if locations[name]==None:
				locations[name]=getGeoCoding(name)
		else:
			locations[name]=getGeoCoding(name)
		return locations

filters=open('filters.txt','r').readline().strip().split('|')
file="pipeFormat.csv"
f=open(file,"r")
headers=f.readline().strip().split('|')
f.close()

def getIndex(s):
    return headers.index(s)


def plotNetworkGraph(year,waveMatrix,locations,nodeNames, filename, nodeSize,targetWeights):
	resolution='f'
	#Bmap_Amplitude = Basemap(projection='merc',llcrnrlon=lower_left_lon,llcrnrlat=lower_left_lat,urcrnrlon=upper_right_lon,urcrnrlat=upper_right_lat,lat_ts=0,resolution=resolution,suppress_ticks=True)
	cmap=plt.get_cmap("jet")
	Bmap_Amplitude=Basemap(projection='merc',llcrnrlat=-61.4,urcrnrlat=71.56,\
			llcrnrlon=-163.7,urcrnrlon=165.65,lat_ts=20,resolution='h')
	G_Amplitude = nx.DiGraph()
	for name in nodeNames:
		latitude=locations[name][0]
		longitude=locations[name][1]
		#print(latitude,longitude)
		x,y=Bmap_Amplitude(longitude,latitude)
		G_Amplitude.add_node(name,pos=(x,y))
	   
	for nm in waveMatrix[year]:
		if nm[0] not in ['','.','0']:

			weight = waveMatrix[year][nm]
			G_Amplitude.add_edge(nm[0], nm[1],weight=weight)

	degree = nx.in_degree_centrality(G_Amplitude)
	betweennes = nx.betweenness_centrality(G_Amplitude)
	closeness = nx.closeness_centrality(G_Amplitude)
	pickle.dump(degree,open('centralityPickles/asup_degree{}.pickle'.format(year),'wb'))
	pickle.dump(betweennes,open('centralityPickles/asup_betweennes{}.pickle'.format(year),'wb'))
	pickle.dump(closeness,open('centralityPickles/asup_closeness{}.pickle'.format(year),'wb'))

	maxDegree = max([j for i,j in degree.items()])
	maxDegreeNodes = ', '.join([i for i,j in degree.items() if j==maxDegree and j!=0.0])
	maxBetween = max([j for i,j in betweennes.items()])
	maxBetweenNodes = ', '.join([i for i,j in betweennes.items() if j==maxBetween and j!=0.0])
	maxClose = max([j for i,j in closeness.items()])
	maxCloseNodes = ', '.join([i for i,j in closeness.items() if j==maxClose and j!=0.0])

	plt.close()
	#plt.axis('off')
	fig, ax = plt.subplots()
	#ax.text(-0.01, 1.02, 'b)', transform=ax.transAxes, size=14,color='purple')

	plt.scatter(-1,-1,label='Max Degree:{}'.format(maxDegreeNodes),color='b',s=3)
	plt.scatter(-1,-1,label='Max Betweeness:{}'.format(maxBetweenNodes),color='b',s=3)
	plt.scatter(-1,-1,label='Max Closeness:{}'.format(maxCloseNodes),color='b',s=3)

	plt.title('Active Support Network: {}'.format(year),fontsize = 9)
	edgewidth_Amplitude = [ d['weight'] for (u,v,d) in G_Amplitude.edges(data=True)]
	pos=nx.get_node_attributes(G_Amplitude,'pos')
	
	nx.draw_networkx_nodes(G_Amplitude,pos, node_color = 'y', node_size = nodeSize, alpha = 0.7)
	#nx.draw_networkx_edges(G_Amplitude, pos, edge_color = edgewidth_Amplitude, width=edgewidth_Amplitude, alpha = edgewidth_Amplitude)
	nx.draw_networkx_edges(G_Amplitude, pos, width=[0.5 for i in edgewidth_Amplitude] ,cmap=cmap,edge_color =  [cmap(i) for i in edgewidth_Amplitude], alpha = [cmap(0.95) for i in edgewidth_Amplitude])

	Bmap_Amplitude.drawcountries()
	Bmap_Amplitude.drawstates()
	#Bmap_Amplitude.bluemarble()
	Bmap_Amplitude.drawlsmask(land_color='white',ocean_color='grey',lakes=True)
	

	plt.legend(loc='lower right',prop={'size': 6})
	plt.axis('off')
	print(year)
	#plt.savefig("paperImages/{}.png".format(year),dpi=600,bbox_inches='tight')
	#plt.show()



# In[9]:

noLabel = ['0','.','-','']
file="pipeFormat.csv"
f=open(file,"r")
activeIndex=getIndex('statesup')
defactoIndex=getIndex('defacto')
print(f.readline())
data=OrderedDict()
noCountry = ['Tajikistan, Kyrgyzstan, Uzbekistan', 'Tajikistan, Kyrgyzstan, Uzbekistan, Pakistan','1',1]
transactions = set()
for l in f:
	row=l.split("|")
	year=int(row[3])
	territory=row[15]
	supportCountry=row[38]
	support = int(row[defactoIndex]) if row[defactoIndex] not in noLabel else 0
	if support >= 1 and territory not in noLabel:
		if  supportCountry not in noCountry and territory not in noCountry:
			if year not in data:
				data[year]={}

			key =(supportCountry,territory,)
			transactions.add(key)
			if key not in data[year]:
				data[year][key] = 0
			data[year][key]+=1
		
   
f.close() 
print(len(transactions))



waveMatrix=data  
nodeSize=1
locations=pickle.load(open("locations.pickle","rb"))
nodeNames=pickle.load(open("nodenames.pickle","rb"))  
targetWeights=pickle.load(open("targetWeights.pickle","rb"))  
filename="plot5"

for year in list(data.keys()):
	if year == 1957:
		print(year)
		
		plotNetworkGraph(year,waveMatrix,locations,nodeNames, filename, nodeSize,targetWeights)
   


