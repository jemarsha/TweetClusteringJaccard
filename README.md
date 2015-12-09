# TweetClusteringJaccard
A good example of how to cluster tweets using the Jaccard Distance Metric

Code is commented for ease of usage by others.

Depending on the command line argument, You've got two ways to run it, either with the initial parameter K as shown in the example below:

python tweet_clustering.py Tweets.json .7 output.txt
output-for-humans.txt

or with the initial seeds file 'InitialSeeds.txt' as shown in this example below:

python tweet_clustering.py Tweets.json InitialSeeds.txt output.txt
output-for-humans.txt

The command line takes as argument the json file of tweets, either the jaccard distance threshold that you want the tweets to have as a distance or a file of initial centroids, an output file for the centroid ids and tweet ids, and another output file for the actual tweets in word format

Command Line prints out an example message should you make a mistake giving details on what to use as input.

The bigger the threshold, the
bigger the distance that is tolerated within a cluster, and with a
bigger distance you get too many tweets in a cluster and too few
clusters.  .7 or .8 seems to work the best and yield the best results with .8 being my threshold of choice.
.1 gives too many clusters while .9 gives too few.

