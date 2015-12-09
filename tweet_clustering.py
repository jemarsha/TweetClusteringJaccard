import os
import math
import string
import itertools
import sys
import codecs






#	jaccard_similarity is used to calculate the distance between tweets.


def jaccard_distance(x, y):
	"""Returns the Jaccard distance (or 1-similarity) between two lists"""
	intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
	union_cardinality = len(set.union(*[set(x), set(y)]))
	return 1-intersection_cardinality/float(union_cardinality)
 

#	K-MEANS CLUSTERING



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


def getRoot(tweet_id, tweets):
	""" Finds the root of the forest of this tweet using path compression """
	if tweets[tweet_id]['centroid'] != tweet_id:
		tweets[tweet_id]['centroid'] = getRoot(tweets[tweet_id]['centroid'], tweets)

	return tweets[tweet_id]['centroid']


def initCentroids(tweets, max_dist):
	""" Initializes the initial centroids based on Kruskal's algorithm by creating
	forests of minimum spanning trees and distances within each forest up to
	max_dist """

	distances = []
	
	for key1 in tweets.keys():
		tweets[key1]['centroid'] = key1
		for key2 in tweets.keys():
			if key1 < key2:
				distances.append([key1, key2, \
					jaccard_distance(tweets[key1]['text'], tweets[key2]['text'])])

	distances.sort(key = lambda distance: distance[2])

	forests = len(tweets)

	for [key1, key2, distance] in distances:
		root1 = getRoot(key1, tweets)
		root2 = getRoot(key2, tweets)
		if root1 != root2:
			if jaccard_distance(tweets[root1]['text'], tweets[root2]['text']) < max_dist:
				tweets[root2]['centroid'] = getRoot(root1, tweets)
				forests -= 1

	# ensure that the centroid is the root of the forest
	for key in tweets.keys():
		getRoot(key, tweets)
	

if __name__ == '__main__':
	count = 0
	if len(sys.argv) != 5:
		print("  Usage: python tweet_clustering.py <tweets> <max_dist>" + \
			" <output> <human-output>")
		print("Example: python tweet_clustering.py Tweets.json 0.7" + \
			" output.txt output-for-humans.txt")

		print("  Usage: python tweet_clustering.py <tweets> <seeds>" + \
			" <output> <human-output>")
		print("Example: python tweet_clustering.py Tweets.json" + \
			" InitialSeeds.txt output.txt output-for-humans.txt")

		sys.exit(0)


	# Import and process tweets
	with open(sys.argv[1], 'r') as f:
		import json
		# The dataset is of the form:
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
			# Split into words and record it in the dataset
			tweets[tweet['id']] = {'text': tweet['text'].split(' '),
								   'centroid': None}

	# Depending on the command line argument, either load the suggested initial
	# centroids from a file, or initialize them from my algorithm
	try:
		initCentroids(tweets, float(sys.argv[2]))
		centroids = list(set([tweets[tweet_id]['centroid'] for tweet_id in tweets.keys()]))
	except ValueError:
		with open(sys.argv[2], 'r') as f:
			centroids = []
			for l in f.readlines():
				ID = int(l.replace(',', ''))
				centroids.append(ID)

	# I run the classification algo
	tweets = kmeans(tweets, centroids)

	# And save the output data
	with open(sys.argv[3], 'w') as f:
		clusters = getClusters(tweets)
		for clusterID in clusters:
            		count += 1
			f.write(str(clusterID) + ": " + ', '.join(map(str, clusters[clusterID])) + '\n')
	print count
        
	    
	# also create a human-readable file 
	with codecs.open(filename=sys.argv[4], mode="w", encoding="utf-8") as f:
		out = ''
		for clusterID in clusters:
			out += 'Centroid: ' +  tweets2[clusterID] + ':\n'
			for elementID in clusters[clusterID]:
				out += tweets2[elementID]+ '\n'
			out += '*'*78 + '\n\n'

		f.write(out)
