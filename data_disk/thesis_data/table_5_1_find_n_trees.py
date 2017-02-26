from __future__ import division
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
import sys, common, os
import itertools

from subprocess import call
from sklearn import model_selection, metrics
from sklearn.ensemble import RandomForestRegressor

def get_predict(clf, Xtrn, Xtst, ytrn, ytst):
	
	clf.fit(Xtrn, ytrn)

	predictions = DataFrame(clf.predict(Xtst), columns=ytrn.columns, index=Xtst.index).fillna(0)
	score = metrics.r2_score(ytst, predictions, multioutput='uniform_average')

	# return (the predictions, a series of rankings from the predictions, r2 score)
	return (predictions,predictions.apply(common.get_strings, axis=1), score)

def evaluate(preds, actual, df):

	data = DataFrame({'actual' : actual, 'preds': preds, 'key':actual.index}) 

	# cumulative time to a Valid or Invalid result
	data['cum time'] = data.apply(lambda ser: 
		common.time_to_valid( ser['preds'], 
			df.ix[ser['key'], common.TIMES+common.RESULTS ] ), axis=1 )
	# cumulative difference in scores for ranking positions
	data['cum score diff'] = data.apply(lambda ser:
		common.sum_score_diff( ser['actual'], ser['preds'], 
		df.ix[ser['key'], common.PROVERS ] ), axis=1)
	# normalised distributed cumulative gain for scoring rankings 
	data['ndcg'] = 	data.apply(lambda ser: 
		common.ndcg_k( ser['actual'], ser['preds'], len(common.PROVERS) ), axis=1)
	# mean average error
	data['mae'] = data.apply(lambda ser:
		common.mae(ser['actual'], ser['preds']), axis=1)	
	
	return {'ndcg': data['ndcg'].mean(), 		# avg ndcg for all predicted rankings  
			'cum time': data['cum time'].mean(),# avg cumulative time to Valid or Invalid
			'MAE': data['mae'].mean(),			# mean mean average error
			'score diff': data['cum score diff'].mean() # regression error: mean diff.
			}

if __name__ == '__main__':

	test = DataFrame.from_csv('whygoal_valid_test.csv').fillna(0)
	# separate input from output
	X = test.drop(common.IGNORE, axis=1)
	y = {}
	for p in common.PROVERS:
		y[p] = test.apply(lambda x:
					# calculate each solver's cost given result, time and timeout 
					#common.new_score_func_single(x[p+' result'], x[p+' time'], 10.0), 
					common.twice_delta_score_func(x[p+' result'], x[p+' time'], 10.0),
					axis=1)
		test[p] = y[p]

	y = DataFrame(y)
	total = []

	strat = model_selection.StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
	bests = y.apply(common.get_strings, axis=1)
	kf = strat.split(X, bests)

	# each fold
	for i, (train_index, test_index) in enumerate(kf):

		X_train, X_test = X.ix[train_index], X.ix[test_index]
		y_train, y_test = y.ix[train_index], y.ix[test_index]

		# the ground truth: 'Best'
		actual = y_test.apply(common.get_strings, axis=1)
		# the reverse of 'Best': 'Worst'
		worst = actual.apply(lambda x: x[::-1])

		models, scores = {}, {}

		for n in range(10,100,10):

			ns = str(n)

			clf = RandomForestRegressor(n_estimators=n, random_state=42, min_samples_leaf=5)
			models[ns] = get_predict(clf, X_train, X_test, y_train, y_test) 
			scores[ns] = models[ns][1]

		table = {ns: evaluate(clf, actual, test)
			for ns, clf in scores.iteritems() }

		for ns, m in models.iteritems():
			table[ns]['score'] = m[2]

		total.append(DataFrame(table).transpose())
		print('Fold '+str(i+1)+' complete')

	cols = (total[0]).columns
	rows = (total[0]).index

	final = {row: {col: np.mean([tbl.ix[row, col] for tbl in total])
					for col in cols}
			for row in rows}
	rv = DataFrame(final).transpose().sort_index()
	
	
	txt = """
\documentclass[]{{article}}
\\usepackage{{booktabs, graphicx}}

\\begin{{document}}

\\begin{{table}}
\caption{{ {title} }}
\\resizebox{{\\textwidth}}{{!}}{{%
{table} }}
\end{{table}}
\end{{document}}

""".format(title='Find n Trees',
	table=rv.ix[:, [1,2,3,0,4]].to_latex(
		float_format=lambda x: "{0:.2f}".format(x) ) )
	
	with open('find_n_trees.tex', 'w') as f:
		f.write(txt)
	
	command = "pdflatex -synctex=1 -interaction=nonstopmode find_n_trees.tex"
	call(command.split(), shell=False)
	os.remove('find_n_trees.aux')
	os.remove('find_n_trees.log')
	os.remove('find_n_trees.synctex.gz')
	# the first few
	print(rv.head(10))
