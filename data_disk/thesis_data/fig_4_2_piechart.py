from __future__ import division
import common, os
from pandas import DataFrame, Series
import matplotlib.pyplot as plt

# find each solver's relative contribution to the portfolio
# this is defined as the cost difference between the best ranking
# without the solver and the best ranking with it. 

df = DataFrame.from_csv('whygoal_stats.csv')
# apply cost function
for p in common.PROVERS:
	df[p] = df[common.RESULTS+common.TIMES].apply(
		lambda ser: common.twice_delta_score_func(ser[p+' result'], ser[p+' time'], 10), axis=1)
df['Best'] = df[common.PROVERS].apply(common.get_strings, axis=1)
# find the best's cost - note that the worst solver is excluded.
# this way, we compare rankings of equal length and df['Best cost'] <= cost[p] for all p
df['Best cost'] = df.apply(lambda ser: common.acc_cost(ser['Best'][:-1], ser[common.RESULTS+common.PROVERS]), axis=1)
cost = {}

total = df['Best cost'].sum() # for every PO
print total

# find the best's cost without solver p
for p in common.PROVERS:
	df['cost excluding '+p] = df.apply(lambda ser: common.acc_cost(ser['Best'], ser[common.RESULTS+common.PROVERS], p), axis=1)
	p_contrib = df['cost excluding '+p].sum()
	# and take total away from it
	cost[p] = p_contrib - total
	#print(p+' contribution: {}'.format(cost[p]))

# normalise
divisor = sum(cost.values())
norms = {p: cost[p]/divisor for p in common.PROVERS}

colors = ['lightpink','orchid','lightsteelblue','cyan','springgreen','olive','orange','red']

print norms.keys()

# plot the pie chart
plt.pie(norms.values(), labels=norms.keys(), colors=colors,
	autopct='%1.1f%%', labeldistance=1.1, pctdistance=0.9, startangle=0)#, textprops={'rotation':90})
plt.axis('equal')

plt.savefig(os.path.join('figures','pie.pdf'),bbox_inches='tight')