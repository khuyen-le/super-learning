from psychopy import visual, event, core, gui, tools
import os
import random
import math

from sklearn_extra.cluster import KMedoids

def get_cluster(array, max_n_cluster): 
    """
    Param: array is an array of tuple
    """
    inertias = []
    for i in range(1,max_n_cluster):
        possible_cluster = KMedoids(n_clusters=i, method='pam').fit(array)
        inertias.append(possible_cluster.inertia_)

    from kneed import KneeLocator
    kl = KneeLocator(range(1, max_n_cluster), inertias, curve="convex", direction="decreasing" )
    
    #refit
    cluster = KMedoids(n_clusters = kl.elbow, method='pam').fit(array)
    return cluster

def test_cluster(cluster, items_list): 
    for idx, cluster_number in enumerate(cluster.labels_):
        if (cluster_number == 0): 
            fillColor = "yellow"
        elif (cluster_number == 1):
            fillColor = 'blue'
        elif (cluster_number == 2):
            fillColor = 'orange'
        elif (cluster_number == 3): 
            fillColor = 'purple'
        elif (cluster_number == 4):
            fillColor = 'red'
        elif (cluster_number == 5): 
            fillColor = 'lightblue'
        elif (cluster_number == 6): 
            fillColor = 'brown' 
        else:
            fillColor = 'gray'
        items_list[idx]['rect'].setFillColor(fillColor)

    for item in items_list: 
        item['rect'].draw()
        item['text_stim'].draw()