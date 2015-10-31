import os
import math
import string
import itertools
import sys
reload(sys)
sys.setdefaultencoding('utf8')

################################################################################
#
#	AUXILIARY FUNCTIONS
#	The functions below are employed by the k-means algorithm.
#
#	jaccard_similarity is used to calculate the distance between tweets.
#
################################################################################

def jaccard_distance(x, y):
	"""Returns the Jaccard distance (or 1-similarity) between two lists"""
	intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
	union_cardinality = len(set.union(*[set(x), set(y)]))
	return 1-intersection_cardinality/float(union_cardinality)
 
################################################################################
#
#	K-MEANS CLUSTERING
#	The functions below implement k-means clustering for a text corpus. 
#
################################################################################

MAX_ITERATIONS = 1000

def shouldStop(oldCentroids, centroids, iterations):
	"""Returns True or False if k-means is done. K-means terminates either
	because it has run a maximum number of iterations OR the centroids
	stop changing."""
	if iterations > MAX_ITERATIONS: return True
	return oldCentroids == centroids

def setLabels(dataSet, centroids):
	"""For each element in the dataset, find the closest centroid."""
	for e in dataSet.values():
		nearestCentroidID = centroids[0]
		nearestCentroid = dataSet[nearestCentroidID]
		minDist = jaccard_distance(e['text'], nearestCentroid['text'])
		for centroidID in centroids[1:]:
			centroid = dataSet[centroidID]
			dist = jaccard_distance(e['text'], centroid['text'])
			if dist < minDist:
				nearestCentroidID = centroidID
				minDist = dist
		# Make that centroid the element's label.
		e['centroid'] = nearestCentroidID
	return dataSet

def getClusters(dataSet):
	"""Iterate through the dataPoints in dataSet and gather them by assigned
	centroid into cluster."""
	clusters = {}
	for elementID in dataSet:
		e = dataSet[elementID]
		if e['centroid'] not in clusters:
			clusters[e['centroid']] = [elementID]
			# The centroid itself is part of the cluster
			clusters[e['centroid']].append(e['centroid'])
		else:
			clusters[e['centroid']].append(elementID)
	return clusters

def getCentroids(dataSet):
	"""Iterate through the dataset centroid by centroid to check if there exists
	a dataPoint that is closer to its neighbors than the centroid itself. If so,
	set that dataPoint as the new cluster centroid""" 
	clusters = getClusters(dataSet)
	# To find a new centroid, find the sum of the distances from one element
	# to the rest. The centroid will have the smallest such sum. 
	newCentroids = []
	for centroid in clusters:
		minTotalDist = 0
		newCentroid = centroid
		for e in clusters[centroid]:
			minTotalDist += jaccard_distance(dataSet[centroid]['text'], dataSet[e]['text'])
		
		for e in clusters[centroid]:
			totalDist = 0
			for e_prime in clusters[centroid]:
				totalDist += jaccard_distance(dataSet[e]['text'], dataSet[e_prime]['text'])
			if totalDist < minTotalDist:
				minTotalDist = totalDist
				newCentroid = e
		newCentroids.append(newCentroid)

	return newCentroids

def kmeans(dataSet, initial_centroids):
	"""Executes the k-means clustering algorithm on a dataSet given an initial
	set of centroids. Returns the same dataSet with each dataPoint labeled by 
	the ID of its cluster's centroid."""
    # Initialize centroids randomly
    k = len(initial_centroids)
    centroids = initial_centroids
    
    # Initialize book keeping vars.
    iterations = 0
    oldCentroids = None
    
    # Run the main k-means algorithm
    while not shouldStop(oldCentroids, centroids, iterations):
        # Save old centroids for convergence test. Book keeping.
        oldCentroids = centroids
        iterations += 1
        
        # Assign labels to each datapoint based on centroids
        dataSet = setLabels(dataSet, centroids)
        
        # Assign centroids based on datapoint labels
        centroids = getCentroids(dataSet)
        
    # We can get the labels too by calling getLabels(dataSet, centroids)
    return dataSet

if __name__ == '__main__':
	# Import and process tweets
	with open('Tweets.json', 'r') as f:
		import json
		# Our dataset is of the form:
		# {ID: {text: [list of tweet words]
		#		centroidID: ID of tweet at centroid cluster
		#	 }
		# }
		tweets = {}
		tweets2 = {}
		exclude = set(string.punctuation)

		for l in f.readlines():
			tweet = json.loads(l)
			tweets2[tweet['id']] = tweet['text']
			# Remove punctuation
			tweet['text'] = ''.join(ch for ch in tweet['text'] if ch not in exclude)
			# Convert to lowercase
			tweet['text'] = tweet['text'].lower()
			# Split into words and record it in our dataset
			tweets[tweet['id']] = {'text': tweet['text'].split(' '),
								   'centroid': None}

	# Now that our data is living in a vector space, we can execute K-means.
	# First, we load the suggested initial centroids:
	with open('InitialSeeds.txt', 'r') as f:
		centroids = []
		for l in f.readlines():
			ID = int(l.replace(',', ''))
			centroids.append(ID)

	# We run the classification algo
	tweets = kmeans(tweets, centroids)

	# And save the output data
	with open('output.txt', 'w') as f:
		clusters = getClusters(tweets)
		for clusterID in clusters:
			f.write(str(clusterID) + ": " + ', '.join(map(str, clusters[clusterID])) + '\n')
	
	# We also create a human-readable file to confirm our algo works. Yay! 
	with open('output-for-humans.txt', 'w') as f:
		out = ''
		for clusterID in clusters:
			out += 'Centroid: ' +  tweets2[clusterID] + ':\n'
			for elementID in clusters[clusterID]:
				out += tweets2[elementID]+ '\n'
			out += '*'*78 + '\n\n'

		f.write(out)