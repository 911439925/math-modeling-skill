# HMML 方法索引

> 本知识库涵盖 98 种建模方案，按 5 个领域组织。使用方法：
> 1. 阅读本索引，根据任务类型定位相关领域
> 2. 只加载相关领域的详细文件（而非全部）
> 3. 按评估维度（假设匹配、结构适配、变量兼容、动态性、可解性）选取 top-6 方法

## 领域列表

### 1. Operations Research (运筹学) — hmml_or.md
**涵盖子领域**: Programming Theory, Graph Theory, Stochastic Programming Theory
**包含方法**: Linear Programming (LP), Integer Programming (IP), Mixed Integer Programming (MIP), Convex Programming, Quadratic Programming (QP), Set Programming, Goal Programming, Multi-Objective Programming, Multi-level Programming, Dynamic Programming (DP), Shortest Path Models (S-T, All-Pair), Eulerian Graph (Euler Path), Hamiltonian Cycle, Traveling Salesman Problem (TSP), Minimum Spanning Tree (MST), Huffman Tree, Steiner Tree, Network Flow Models (Max-Flow/Min-Cost Max-Flow), Matching Problem, Graph Coloring, Covering Models, Algebraic Representation of Graphs (Adjacency Matrix, Laplacian Matrix), Queuing Theory, Inventory Theory, Decision Theory, Statistics
**适用场景**: 资源分配、路径优化、网络设计、调度问题、排队系统、库存管理

### 2. Optimization Methods (优化方法) — hmml_optimization.md
**涵盖子领域**: Deterministic Algorithms, Heuristic Algorithms, Iterative Algorithms, Constrained Optimization, Solving Techniques
**包含方法**: Greedy Algorithm, Divide and Conquer, Local Search, Tabu Search (TS), Genetic Algorithm (GA), Immune Algorithm (IA), Simulated Annealing (SA), Particle Swarm Optimization (PSO), Ant Colony Optimization (ACO), Newton Method/Quasi-Newton Methods, Conjugate Gradient Method (CGM), Golden-Section Search, Linear Programming (约束优化视角), Feasible Direction Method, Projected Gradient Method, Branch and Bound Method, Relaxation, Restriction, Penalty Function, Duality, Lagrange Multiplier, Karush-Kuhn-Tucker (KKT) Conditions, Back Propagation Neural Network (BP Neural Network)
**适用场景**: 组合优化、函数优化、工程参数调优、机器学习超参数优化、约束求解

### 3. Machine Learning (机器学习) — hmml_ml.md
**涵盖子领域**: Classification, Clustering, Regression, Dimensionality Reduction (Linear/Nonlinear), Ensemble Learning
**包含方法**: K-Nearest Neighbors (KNN), Decision Tree, Random Forest, Support Vector Machine (SVM), Linear Discriminant Analysis (LDA), Logistic Regression, Naive Bayes, K-Means Algorithm (K-Means++), Expectation Maximization (EM), Self-Organizing Maps (SOM), Hierarchical Clustering, Linear Regression, Locally Weighted Linear Regression (LWLR), Ridge Regression, Poisson Regression, Canonical Correlation Analysis (CCA), Principal Component Analysis (PCA), Local Linear Embedding (LLE), Laplacian Eigenmaps, Kernel Function, Boosting Algorithm, Bagging Algorithm
**适用场景**: 分类预测、聚类分析、回归建模、特征降维、数据可视化、异常检测

### 4. Prediction (预测方法) — hmml_prediction.md
**涵盖子领域**: Discrete Prediction, Continuous Prediction (Time Series Models, Differential Equations)
**包含方法**: Markov Decision Process (MDP), Grey Forecasting, Bayesian Network, Difference Equation, ARIMA Model, GARCH Model (EGARCH variant), Infectious Disease Model (SIR/SEIR/SIRS), Population Prediction Model, Economic Growth Model, River Pollutant Diffusion Model, Battle Model, Heat Conduction Model
**适用场景**: 时间序列预测、金融风险建模、疫情传播预测、人口预测、经济增长预测、环境建模、军事对抗分析

### 5. Evaluation Methods (评价方法) — hmml_evaluation.md
**涵盖子领域**: Scoring Evaluation, Statistical Evaluation, Goodness of Fit Test
**包含方法**: Fuzzy Comprehensive Evaluation, Grey Evaluation, Analytic Hierarchy Process (AHP), Analytic Network Process (ANP), Data Envelopment Analysis (DEA), TOPSIS, Entropy Weight Method, Information Entropy Method, Pearson Correlation Coefficient Test, Wilcoxon's Signed Rank Test, Kendall's Coefficient of Concordance Test, Analysis of Variance (ANOVA), Chi-Square Goodness-of-Fit Test, Kolmogorov-Smirnov Test (KS Test)
**适用场景**: 多指标综合评价、权重确定、效率分析、相关性检验、模型拟合度检验、方案优选

## 常见方法组合模式

| 组合类型 | 方法组合 | 适用场景 |
|---------|---------|---------|
| 综合评价 | AHP + 熵权法 + TOPSIS | 多指标体系评价 |
| 综合评价 | 灰色关联 + 优劣解距离 | 小样本数据评价 |
| 综合评价 | 模糊综合 + 层次分析 | 定性定量混合评价 |
| 权重确定 | AHP + 熵权法(组合赋权) | 主客观权重融合 |
| 预测 | ARIMA + LSTM 混合 | 时序预测(趋势+非线性) |
| 预测 | 灰色预测 + 马尔可夫 | 小样本趋势预测 |
| 优化 | 遗传算法 + 模拟退火 | 复杂组合优化 |
| 优化 | MDP + 启发式算法 | 多阶段决策优化 |
| 效率评价 | DEA + AHP | 相对效率+权重分析 |
| 分类 | SVM + PCA | 高维数据分类 |
| 聚类 | K-Means + 层次聚类 | 分群/市场细分 |
