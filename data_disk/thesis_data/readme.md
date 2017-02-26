# Predicting SMT Solver Performance for Software Verification
## Andrew Healy
### [Principles of Programming](http://www.cs.nuim.ie/research/pop/) Research Group, Dept. of Computer Science, Maynooth University, Ireland


Measuring 8 SMT solvers' performance on the
[Why3](http://why3.lri.fr/) examples dataset. We record the result returned by [Alt-Ergo](https://alt-ergo.ocamlpro.com/) (versions 0.95.2 and 1.01), [CVC3](http://www.cs.nyu.edu/acsys/cvc3/), [CVC4](http://cvc4.cs.nyu.edu/web/), [veriT](http://www.verit-solver.org/), [Yices](http://yices.csl.sri.com/), and [Z3](https://github.com/Z3Prover/z3) (versions 4.3.2 and 4.4.1). We also measure the time taken
by the solver to return the result. A Random Forest model is chosen and evaluated.

Python libraries we use: [Pandas](http://pandas.pydata.org/), [Numpy](http://www.numpy.org/), [Sci-kit Learn](http://scikit-learn.org/dev/index.html), [Matplotlib](http://matplotlib.org/). All Python files can be run on the command line in the usual way: eg `python <filename.py>`

### Directory descriptions

#### `figures/`
Where all figures for the thesis are stored

#### `data/`
This folder contains a subfolder for each file in the examples repository. Each folder contains:
 - `<name>.mlw` the WhyML file sent to Why3
 - `<name>.json` a JSON dictionary containing timings and results for various timeout values
 - `stats.json` the syntacic features statically extracted from `<name>.mlw`  (used as independent variables for prediction)
 - `split/` folder containing the resultant goals after applying the Why3 transformation `split_goal_wp` to each file `.mlw`. file. Created by `split_goal.py`  

#### `benchexec/`
Python interface to the [Benchexec](https://github.com/sosy-lab/benchexec) measurement framework. See `LICENCE_benchexec.txt` for licence.

### Modules referenced for their methods and/or data

#### `common.py`
A collection of short, commonly-used constants and functions used by many of the other Python scripts.

#### `provable_files.py`
A static collection of a provable files in the test set. Used by `fig_6_3_linegraph.py` to construct the linegraph describing Where4 and the theoretical strategies' performance on the test dataset.

### Data preparation and smaller operations

#### `create_stats_df.py`
Collect data from the JSON files and combine it with the syntax metrics. Save the data as `whygoal_stats.csv`

#### `permute_rankings.py`
Find values for the 'Random' strategy (either train or test) by averaging values for all possible rankings. Is slow because it has 8! rankings to get through.

#### `test_time.py`
An example of how the Benchexec framework is used to measure the CPU time consumed by each SMT solver.

#### `split_goal.py`
An application of the Why3 transformation `split_goal_wp` applied to every `.mlw` in order to count the number of simplified goals which could be created by this tactic.

### Pertaining to specific figures and tables

#### `ch3_example_timings.py`
An example of how confidence intervals are used to account for random measurement error when recording the time taken for a Why3 solver call to finish.

#### `collect_data_fig_3_6_table_4_1.py`
Python script to collect data from the JSON files. Results printed for Table 1 and saved to `fig_3_6_data.csv` to be read in by `fig_3_6_barchart.py`

#### `fig_3_6_barchart.py`
Make the first figure (stacked barcharts - 60 second timeout). Uses `fig_3_6_data.csv`. Renders `barcharts.pdf` to `figures` folder

#### `fig_3_7_linegraph.py`
Use the entire dataset to plot the cumulative time taken for Valid/Invalid/Unknown answers to be returned. Renders `line_graph.pdf` to `paper` folder and prints values for the 99th percentile.

#### `table_4_4_compare_regressors.py`
Perform KFold cross-validation on the training set to compare a number of regressor implementations from Sci-kit Learn. Renders `table_4_4_compare_regressors.pdf`

#### `table_5_1_find_n_trees.py`
Perform KFold cross-validation on the training set to compare a 10 Random Forests. The number of Decision Trees in each forest increases by 10 (from 10 to 100). Renders `table_5_1_find_n_trees.pdf`

#### `print_table_6_1_fig_6_1.py`
Outputs several data files used in the Evaluation section:
- `forest.json`: a JSON representation of the trained random forest - suitable for use when compiling the OCaml binary
- `fig_6_1_data.csv`: results for each prover and strategy for the test goals
- `fig_6_3_data.csv`: how long each strategy took to return a Valid/Invalid answer for the test set
- `feature_importances.txt`: These relevance metrics are computed by Sci-kit Learn's Random Forest implementation: they describe the proportion of decisions based on each input variable across all decision trees in Where4's random forest.

#### `fig_6_1_barchart.py`
Renders `barcharts2.pdf` to the `figures` folder. Similar to `fig_3_6_barchart.py` but reads from `fig_6_1_data.csv` and includes theoretical strategies and Where4 results (result of choosing the __first__ solver in each ranking).

#### `fig_6_3_linegraph.py`
The cumulative time taken for the three theoretical strategies and Where
to find an answer to the goals in the test dataset. Uses data stored in `fig_6_3_data.csv` - particularly important for the time-consuming 'Random' calculations. Renders `line_graph_eval_provers.pdf` to the `figures` folder. Also prints the average times File/Theory/Goal times used in Table 6.1.

#### `fig_6_2_thresholds.py`
Parameterise Where4's performance by using a threshold, reading data from `fig_6_3_data.csv`. Renders `thresholds.pdf` to `figures` folder.
These plots show the effect of the threshold on the time taken for a response (top) and number of goals which can be proved (bottom).

### Comma-separated data files

#### `whygoal_test.csv`, `whygoal_valid_test.csv`
Disjoint partitions of `whygoal_stats.csv` for testing (25%) and training/validation (75%) respectively
