import json, common, itertools
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from sklearn import metrics
from sklearn.ensemble import RandomForestRegressor
from sklearn import model_selection

"""
Outputs a datafile for the determination of a threshold used during evaluation

Andrew Healy, feb. 2017
"""

def take_better(res1, res2):
	order = ['Valid', 'Invalid', 'Unknown', 'Timeout', 'Failure']
	for a in order:
		if a in [res1, res2]:
			return a
	return order[-1]

train, test = model_selection.train_test_split(DataFrame.from_csv('whygoal_valid_test.csv').fillna(0), test_size=0.1, random_state=42)

print('Test: '+str(test.shape))
print('Train: '+str(train.shape))
rf = RandomForestRegressor(n_estimators=50,random_state=42,min_samples_leaf=5)
X = train.drop(common.IGNORE, axis=1)
y = {}
for p in common.PROVERS:
	y[p] = train.apply(lambda x:
				common.new_score_func_single(x[p+' result'], x[p+' time'], 10.0),
				axis=1)
	train[p] = y[p]

y = DataFrame(y)
rf.fit(X, y)


# now for testing stuff

#test = train.sample() DataFrame.from_csv('whygoal_valid_test.csv').fillna(0)

X_test = test.drop(common.IGNORE, axis=1)
y_test = {}

# what is each solver's score on the test data?
for p in common.PROVERS:
	y_test[p] = test.apply(lambda x:
				#common.new_score_func_single(x[p+' result'], x[p+' time'], 10.0),
				common.twice_delta_score_func(x[p+' result'], x[p+' time'], 10.0),
				axis=1)
	test[p] = y_test[p]

y_test = DataFrame(y_test)
# save the cost predictions for each goal
test = pd.concat([ test,
					DataFrame(rf.predict(X_test),
						columns=['Predicted '+c for c in y.columns],
						index=X_test.index ).fillna(0) ],
				axis=1)
# and turn them into rankings
predictions = DataFrame(rf.predict(X_test), columns=y.columns, index=X_test.index ).fillna(0)
pred_ranks = predictions.apply(common.get_strings, axis=1)

actual = y_test.apply(common.get_strings, axis=1)
worst = actual.apply(lambda x: x[::-1])

output = {	'Valid':common.is_valid,
			'Invalid':common.is_invalid,
			'Unknown':common.is_unknown,
			'Timeout':common.is_timeout,
			'Failure':common.is_error}

# count the results for each prover/goal
results = {p :
			{o: train.apply(lambda ser: fun(ser[p+' result']), axis=1).sum()
			for o, fun in output.iteritems() }
		for p in common.PROVERS }

# how many of each are there?
print('files: {}\ntheories: {}\ngoals: {}'.format(
	len(test['file'].unique()),
	len(test['theory'].unique()),
	len(test['goal'].unique())
	))

test['key'] = test.index
test['rf'] = pred_ranks
test['best'] = actual
test['worst'] = worst

# add results and times for strategies and where4
for x in ['best', 'worst']:

	test[x+' time'] = test.apply(lambda ser: common.time_to_valid( ser[x],
				test.ix[ser['key'], common.TIMES+common.RESULTS ] ), axis=1 )
	test[x+' result'] = test.apply(lambda ser: common.best_result_from_rank( ser[x],
				test.ix[ser['key'], common.RESULTS ] ), axis=1 )

test['rf time'] = test.apply(lambda ser: common.time_to_valid_ae( ser['rf'],
			test.ix[ser['key'], common.TIMES+common.RESULTS ] ), axis=1 )
test['rf result'] = test.apply(lambda ser: common.best_result_from_rank_ae( ser['rf'],
			test.ix[ser['key'], common.TIMES+common.RESULTS ] ), axis=1 )

test['rf no time'] = test.apply(lambda ser: common.time_to_valid( ser['rf'],
			test.ix[ser['key'], common.TIMES+common.RESULTS ] ), axis=1 )
test['rf no result'] = test.apply(lambda ser: common.best_result_from_rank( ser['rf'],
			test.ix[ser['key'], common.TIMES+common.RESULTS ] ), axis=1 )




test.to_csv('thresholds_using_training.csv')
