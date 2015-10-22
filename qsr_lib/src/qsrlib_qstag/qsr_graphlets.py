#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Compute QSTAG Graphlets
	__author__	  = "Paul Duckworth"
	__copyright__   = "Copyright 2015, University of Leeds"
"""
from __future__ import print_function
import sys
import itertools

def compute_graphlets(episodes):
	""" This function implements Krishna's validity criteria to select all valid
	graphlets from an activity graph: see Sridar_AAAI_2010 for more details.
	"""

	print("Called compute_graphlets...")
	print("num of episodes:", len(episodes))

	episode_ids  = {}
	intervals = {}

	print("all episodes: ", episodes)

	# Gather the episodes and interval data
	for ep_id, ep in enumerate(episodes):
		print("\nID:", ep_id, ep)

		ep_start = ep[2][0]
		ep_end   = ep[2][1]

		# Use codes for the episodes throughout the function
		# At the end we replace the codes with episodes
		episode_ids[ep_id]  = ep


		episode_data = [ep_start, ep_end, ep_id]
		print(episode_data)

		#todo: add more than two objects
		objs = (ep[0][0], ep[0][1])

		if objs not in intervals: intervals[objs] = [episode_data]
		else: intervals[objs].append(episode_data)
	print("\nepisode_ids: ", episode_ids)
	print("\nintervals: ", intervals)


	graphlets = {}
	graphlets_list = []

	min_rows = 1
	max_rows = 1
	max_episodes = 2
	range_of_rows = range(min_rows, max_rows+1)
	r = 1
	#todo: all r in range_of_rows

	# Once we select the number of rows, find all combinations of rows of r.
	for obj_pair_comb in itertools.combinations(intervals.keys(), r):
		print("object_rows: ", obj_pair_comb)

		# Collect intervals from episodes of relevant rows
		relevant_episodes=[]
		for obj_pair in obj_pair_comb:
			relevant_episodes.extend(intervals[obj_pair])

		print("relevant_episodes", relevant_episodes)

		if relevant_episodes != []:
			interval_breaks = get_temporal_chords_from_episodes(relevant_episodes)
		else:
			#Covers the case where no episodes are added. i.e. episodes that do not start at frame 1.
			interval_breaks = []
		print("interval_breaks: ", interval_breaks)

		num_of_interval_breaks = len(interval_breaks)
		print('Length of episodes:', num_of_interval_breaks)

		# Loop through this broken timeline and find all
		# combinations (r is from 1 to num_of_intervals)
		# of consecutive intervals (intervals in a stretch).
		for k in xrange(1, num_of_interval_breaks+1):
			for l in xrange(num_of_interval_breaks):
				# Find the combined interval of this combination of intervals
				selected_intervals = interval_breaks[l:l+k]
				# Get the relations active in this active interval
				selected_relations = [m[2] for m in selected_intervals]
				# Some episodes are repeated as they are active in two or more intervals.
				# So remove the duplicates .
				selected_relations_set = tuple(set(itertools.chain.from_iterable(selected_relations)))
				print("eps:", selected_relations_set)
				#Only allow Graphlets of the specified number of Rows. Not all rows.
				if hash(selected_relations_set) not in graphlets:
					graphlets[hash(selected_relations_set)] = selected_relations_set

	#todo: this is outside of the "for r" loop:
	print("\nepisode combinations:", graphlets)

	# Replace the codes with the episodes and return as a list instead of dictionary
	for hash_key in graphlets:
		graphlet_episodes = []
		codes = graphlets[hash_key]
		for epi_code in codes:
			graphlet_episodes.append(episode_ids[epi_code])

		#Remove graphlets that have only one spatial relation - i.e. no temporal relation
		#if len(graphlet_episodes) <= 1:
		#	continue
		#	print hash_key
		#	print len(graphlet_episodes)
		#	print graphlets[hash_key]
		#	print graphlet_episodes
		#	print max_episodes

		if len(graphlet_episodes) <= max_episodes:
			graphlets_list.append(graphlet_episodes)

	print("List of Graphlet selections:")
	for graphlet in graphlets_list:
		print(graphlet)
	sys.exit(1)
	return



def get_temporal_chords_from_episodes(episodes):
	interval_data   = {}
	interval_breaks = []
	# For each time point in the combined interval, get the state of the
	# system which is just a list of relations active in that time point.

	#todo: can this work with floats? Not unless there is a measure of unit.
	for (s, e, id_) in episodes:
		for i in range(int(s), int(e+1)):
			if i not in interval_data:
				interval_data[i] = []
			interval_data[i].append(id_)

	keys = interval_data.keys()
	keys.sort()

	# Now based on the state changes, break the combined interval
	# whenever there is a chage in the state
	start = keys[0]
	interval_value = interval_data[start]
	for i in keys:
		if interval_value == interval_data[i]:
			end = i
			continue
		else:
			interval_breaks.append([start, end, interval_value])
			start = i
			end   = i
			interval_value = interval_data[start]
	else:
		# Adding the final interval
		interval_breaks.append([start, end, interval_value])
	return interval_breaks
