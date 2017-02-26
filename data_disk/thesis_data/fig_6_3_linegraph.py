import common, os, provable_files
import numpy as np
from pandas import DataFrame, Series 
import matplotlib.pyplot as plt

"""
Plot the cumulative time taken for the three theoretical strategies and Where
to find an answer to the goals in the test dataset

Andrew Healy, Aug. 2016
"""

test = DataFrame.from_csv('fig_6_3_data.csv')


total = {}
fig = plt.figure()
fig.set_size_inches(9, 5, forward=True)

ax = fig.add_subplot(1,1,1)

styles = {p : ['-.c','-c','--c', ':c', '-r'][i] for i, p in enumerate(['best', 'rf', 'worst', 'rand', 'rf no'])}
label_map = {l:['Best','Where4 (PS)', 'Worst', 'Random', 'Where4 (no PS)'][i] for i,l in enumerate(['best', 'rf', 'worst', 'rand', 'rf no'])}


for p in ['best', 'rf', 'worst', 'rand', 'rf no']:
	
	label = label_map[p]
	prover = p
	
	# sorted by increasing time taken to return a response
	sorted_times = test[['best result', prover+' time']].sort_values(by=[prover+' time'])
	# find just the Valid/Invalid responses
	good_times = sorted_times.apply(lambda ser: ser['best result'] in ['Valid', 'Invalid'], axis=1)
	# and take these times
	actual_times = sorted_times.loc[good_times]
	
	# incrementing the y axis
	total[p] = Series([x+1 for x in range(actual_times.shape[0])], index=actual_times[prover+' time'])
	ax.plot(total[p].index, total[p].values, styles[p], label=label+': {:.2f} secs'.format(total[p].index[-1]))

	####### print average times ###########
	print 'Goal: '+str(actual_times.mean())
	proved_files = test.apply(lambda ser: ser['file'] in provable_files.f_provable, axis=1)
	actual_times = sorted_times.loc[proved_files]
	print 'File: '+str(actual_times.mean())

	proved_files = test.apply(lambda ser: ser['theory'] in [x[1] for x in provable_files.t_provable]
													and ser['file'] in [x[0] for x in provable_files.t_provable], axis=1)
	actual_times = sorted_times.loc[proved_files]
	print 'Theory: '+str(actual_times.mean())


ax.set_xscale('log',basex=2)
ax.set_ylabel('Number of Valid/Invalid responses')
ax.set_xlabel('Time (log 2 secs)')
ax.legend(loc='lower right', ncol=2, bbox_to_anchor=(1, 1.05))
plt.savefig(os.path.join('figures','line-graph-eval-provers.pdf'), bbox_inches='tight')
fig.show()
