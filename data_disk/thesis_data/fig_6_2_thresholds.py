import pandas as pd
from pandas import DataFrame
import common, sys,os
import matplotlib.pyplot as plt

"""
parameterise Where4's performance by using a threshold.
These plots show the effect of the threshold on the time taken for a response(top)
and number of goals which can be proved (bottom)

Andrew Healy, Aug. 2016
"""

REDONE = True

if REDONE:
	test = DataFrame.from_csv('thresholds_using_training.csv')#('fig_6_3_data.csv')#('data_for_second_linegraph.csv')
else:
	test = DataFrame.from_csv('fig_6_3_data.csv')

def make_triple(ser, thresh, ps=True):
	"""Where's (predicted ranking, result, time) given a goal and threshold"""
	if ps:
		rank = ''.join([ j for j in ser['rf']
			if ser['Predicted '+common.REV_MAP[j]] <= thresh])
		return (rank,
			common.best_result_from_rank_ae(rank, ser),
			common.time_to_valid_ae(rank, ser))
	else:
		rank = ''.join([ j for j in ser['rf']
			if ser['Predicted '+common.REV_MAP[j]] <= thresh])
		return (rank,
			common.best_result_from_rank(rank, ser),
			common.time_to_valid(rank, ser))


# appoximation of each solver's intersection with the threshold line
def find_intersection(val, arr):
	"""	The x locations for the horizontal line segments"""
	lower, upper = -1, 0
	for a in arr:
		if a > val:
			return lower-0.5, upper+0.5
		lower += 1
		upper += 1
	return lower, upper

# add the effect of the threshold i to the data
test = pd.concat([DataFrame([ test.apply(lambda ser:
		make_triple(ser, i),
	axis=1)
	for i in xrange(21) ]).T, test], axis=1)

test = pd.concat([DataFrame([ test.apply(lambda ser:
		make_triple(ser, i, False),
	axis=1)
	for i in xrange(21) ]).T, test], axis=1)

# get the ranks and add to dataframe
ranks = DataFrame({'ranks '+str(i): test.apply(lambda ser:
		''.join([j for j in ser['rf']
			if ser['Predicted '+common.REV_MAP[j]] <= i ]), axis=1)
		for i in xrange(21) })

test = pd.concat([test, ranks], axis=1)

styles = {p : [('lightpink', 'o'),('orchid','^'),('lightsteelblue','s'),('cyan','x'),('springgreen','+'),
				('olive','h'),('orange','D'),('red','*')][i] for i, p in enumerate(common.PROVERS)}

# what are the results at each threshold?
results = DataFrame({'results '+str(i): test.apply(lambda ser:
		common.best_result_from_rank_ae(ser['ranks '+str(i)], ser), axis=1)
		for i in xrange(21) })

results_nops =  DataFrame({'results no ps '+str(i): test.apply(lambda ser:
		common.best_result_from_rank(ser['ranks '+str(i)], ser), axis=1)
		for i in xrange(21) })

# and how long does each take?
times = DataFrame({'times '+str(i): test.apply(lambda ser:
		common.time_to_valid_ae(ser['ranks '+str(i)], ser), axis=1)
		for i in xrange(21)})

times_nops = DataFrame({'times no ps '+str(i): test.apply(lambda ser:
		common.time_to_valid(ser['ranks '+str(i)], ser), axis=1)
		for i in xrange(21)})


# add all these to the dataframe
test = pd.concat([test, results, times, results_nops, times_nops], axis=1)

fig, axes = plt.subplots(ncols=1, nrows=2)#, sharex=True)
fig.set_size_inches(6,10)
fig.subplots_adjust(hspace=0.25)

# the top plot is time
ax = axes[0]
ax.set_xticks([x*2 for x in range(11)])
ax.set_xlabel('Cost threshold for Where4')
#ax.set_title('a')
# the average time for all goals in test at each threshold
ax.plot(range(21), [test['times '+str(i)].mean() for i in range(21)], '-k', label='Where4 (PS)')
ax.plot(range(21), [test['times no ps '+str(i)].mean() for i in range(21)], '-r', label='Where4 (no PS)')

if not REDONE:
	ax.plot((7, 7), (18, 0), '--r', label='threshold')

for p in common.PROVERS:
	# the time that each prover took on average
	t = test[p+' time'].mean()
	print p, ' : ', str(t)
	# draw line segment
	ax.plot(find_intersection(t, [test['times no ps '+str(i)].mean() for i in range(21)]) ,(t,t) , alpha = 0.5 , color=styles[p][0], marker=styles[p][1], mec=styles[p][0], label=p)

ax.set_ylabel('A: Time for any response (secs)')

# bottom plot is number proved
ax = axes[1]
ax.plot( range(21), [len( test.loc[
		test.apply(lambda ser: ser['results '+str(i)] in ['Valid', 'Invalid'], axis=1) ] )
	for i in range(21) ], '-k', label='Where4 (PS)' )
ax.plot( range(21), [len( test.loc[
		test.apply(lambda ser: ser['results no ps '+str(i)] in ['Valid', 'Invalid'], axis=1) ] )
	for i in range(21) ], '-r', label='Where4 (no PS)' )

if not REDONE:
	ax.plot((7, 7), (200, 0), '--r', label='threshold')

for i in range(20):
	print 'threshold = ', str(i), ': ', str(len(test.loc[test.apply(lambda ser: ser['results '+str(i)] in ['Valid','Invalid'], axis=1)])), ' in ', str(test['times '+str(i)].mean())

if REDONE:
	intersect = ['Z3-4.4.1', 'CVC4', 'Alt-Ergo-1.01']
else:
	intersect =  ['Alt-Ergo-1.01']

for p in common.PROVERS:

	# the proved goals
	good_times = test.apply(lambda ser: ser[p+' result'] in ['Valid', 'Invalid'], axis=1)
	# take the proved ones
	actual_times = test.loc[good_times]
	# plot how many there are
	
	l, r = find_intersection(actual_times.shape[0], [len( test.loc[
		test.apply(lambda ser: ser['results no ps '+str(i)] in ['Valid', 'Invalid'], axis=1) ] )
			for i in range(21) ])
	if p in intersect:
		t = (l-1.5, r-0.5)
	else:
		t = (l-0.5, r-0.5)

	ax.plot(t, (actual_times.shape[0], actual_times.shape[0]), alpha = 0.5 , color=styles[p][0], marker=styles[p][1], mec=styles[p][0], label=p)


ax.set_ylabel('B: Number of Valid/Invalid responses')
ax.set_xlabel('Cost threshold for Where4')
ax.set_xticks([x*2 for x in range(11)])
#ax.set_title('b')
ax.legend( loc='upper center', ncol=3,
	 bbox_to_anchor=(0.5, 2.65))
if REDONE:
	plt.savefig('fig_6_2_thresholds_redone.pdf', bbox_inches='tight')
else:
	plt.savefig('fig_6_2_thresholds.pdf', bbox_inches='tight')
