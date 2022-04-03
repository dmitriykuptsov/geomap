import numpy as np
from numpy import random
from sys import maxint
import math
import decimal
from numpy import linalg

class KMeansClustering:
	def __init__(self):
		pass
	@staticmethod
	def distanceEuclidean(x, y):
		return linalg.norm(y-x);
	@staticmethod
	def distanceHaversine(a, b):
		lat = [a[0], b[0]];
		lng = [a[1], b[1]];
		R = 6378137;
		dLat = (lat[1]-lat[0]) * decimal.Decimal(math.pi) / 180;
		dLng = (lng[1]-lng[0]) * decimal.Decimal(math.pi) / 180;
		a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(lat[0] * \
			decimal.Decimal(math.pi) / 180 ) * \
			math.cos(lat[1] * decimal.Decimal(math.pi) / 180 ) * \
			math.sin(dLng/2) * math.sin(dLng/2);
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
		return R * c;

	def clusterCommon(self, x, y, ids):
		seen_clusters = dict();
		seen_centroids = dict();
		centroids = list();
		clusters = list();
		cluster = 0;
		for i in range(0, len(ids)):
			key = str(x[i]) + "," + str(y[i]);
			if key not in seen_clusters.keys():
				seen_clusters[key] = cluster;
				seen_centroids[key] = [x[i], y[i]];
				cluster += 1;

		for i in range(0, len(ids)):
			key = str(x[i]) + "," + str(y[i]);
			#if key not in seen_clusters.keys():
			clusters.append(seen_clusters[key]);
			centroids.append(seen_centroids[key]);

		return {
			'clusters' : clusters,
			'centroids' : centroids
			};


	def clusterRandomCentroids(self, x, y, k = 2, iterations = 1):
		X=np.array(list(zip(x,y)), dtype=np.dtype(decimal.Decimal));
		centroidsIndecies = np.sort(random.choice(len(x), k, replace=False));
		centroids = np.copy(X[centroidsIndecies] * decimal.Decimal(1.0));
		return self.clusterPredifinedCentroids(X, centroids, iterations);
	# not properly tested code
	def clusterPredifinedCentroids(self, X, centroids, iterations = 1):
		k = len(centroids);
		x = X[:, 1];
		clusters  = np.zeros(len(x), dtype=np.dtype(int));
		rijFinal = np.zeros((len(x), k), dtype=np.dtype(decimal.Decimal));
		for l in range(0, iterations):
			rij = np.zeros((len(x), k), dtype=np.dtype(decimal.Decimal));
			for i in range(0, len(x)):
				minCentroid = maxint;
				xij = X[i];
				minj = 0;
				for j in range(0, k):
					centroid = centroids[j];
					d = KMeansClustering.distanceHaversine(xij, centroid);
					if d < minCentroid:
						minj = j;
						minCentroid = d;
				rij[i, minj] = 1;
			clustersToRemove = [];
			centroidsNew = [];
			rijFinal = rij;
			rijToRemove = [];
			for j in range(0, k):
				count = 0.0;
				sumj = np.zeros((1, 2), dtype=np.dtype(decimal.Decimal));
				for i in range(0, len(x)):
					count += rij[i, j];
					sumj += X[i, :] * rij[i, j];
				# Can we compute the centroid like this since we are on the surface of a sphere/geoid?
				if count != 0:
					centroids[j] = sumj / decimal.Decimal(count);
					centroidsNew.append(centroids[j]);
				else:
					rijToRemove.append(j);
			centroids = np.copy(centroidsNew);
			count = 0;
			for i in range(0, len(rijToRemove)):
				index = rijToRemove[i];
				rijFinal = np.delete(rijFinal, index - count, 1);
				count += 1;
			k = len(centroids);
		centroids_out = np.zeros((len(x), 2), dtype=np.dtype(decimal.Decimal));
		# Iterate over all points
		for i in range(0, len(x)):
			l = 0;
			# Iterate over all clusters for a give point
			for j in range(0, k):
				# Assign centroid based on the current cluster number
				# If the cluster for point is 0 skip the assignment and increase the centroid counter l
				# else use the current centroid counter l, asign values and break the loop for the current point
				if rijFinal[i, j] != 0:
					clusters[i] = int(j + 1);
					centroids_out[i] = centroids[l];
					break;
				l += 1;
		return {
			'clusters' : clusters,
			'centroids' : centroids_out
			};
#kmeans = KMeansClustering();
#print kmeans.clusterRandomCentroids(np.array([
#		decimal.Decimal(2.2), 
#		decimal.Decimal(2.2), 
#		decimal.Decimal(2.0), 
#		decimal.Decimal(5.0), 
#		decimal.Decimal(24.0),
#		decimal.Decimal(21.0)]), 
#	np.array([decimal.Decimal(1.2), 
#		decimal.Decimal(1.2), 
#		decimal.Decimal(6), 
#		decimal.Decimal(15), 
#		decimal.Decimal(4),
#		decimal.Decimal(4)]), 5, 10);
