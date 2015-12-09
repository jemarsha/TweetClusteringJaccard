# TweetClusteringJaccard
A good example of how to cluster tweets using the Jaccard Distance Metric. You can run this using any properly formatted json file
from Twitter and gain significant insight on whatever information you are looking for on twitter! Enjoy 

Code is commented for ease of usage by others. I have included several files to see how the output looks.  The InitialSeeds.txt
file and the Tweets.Json file go together from the Boston Marathon.  The OregonShootingTweets.json file goes with the OutputinWords.txt file
and outputbyCentroid.txt file.

Depending on the command line argument, You've got two ways to run it, either with the initial parameter K as shown in the example below:

python tweet_clustering.py Tweets.json .7 output.txt
output-for-humans.txt

or with the initial seeds file 'InitialSeeds.txt' as shown in this example below:

python tweet_clustering.py Tweets.json InitialSeeds.txt output.txt
output-for-humans.txt

The command line takes as argument the json file of tweets, either the jaccard distance threshold that you want the tweets to have as a distance or a file of initial centroids (meaning that you can only have at most that many centroids if you use an input file of centroids), an output file for the centroid ids and tweet ids, and another output file for the actual tweets in word format

Command Line prints out an example message should you make a mistake giving details on what to use as input.

The bigger the threshold, the
bigger the distance that is tolerated within a cluster, and with a
bigger distance you get too many tweets in a cluster and too few
clusters.  .7 or .8 seems to work the best and yield the best results with .8 being my threshold of choice.
.1 gives too many clusters while .9 gives too few.

