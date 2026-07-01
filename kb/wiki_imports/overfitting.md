# Wikipedia Import: Overfitting

## Matched Term

Overfitting

## Domain

contraindications_uncertainty

## Source

https://en.wikipedia.org/wiki/Overfitting

## Description



## Summary

In mathematical modeling, overfitting is the production of an analysis that corresponds too closely or exactly to a particular set of data, and may therefore fail to fit to additional data or predict future observations reliably. An overfitted model is a mathematical model that contains more parameters than can be justified by the data. In the special case of a model that consists of a polynomial function, these parameters represent the degree of a polynomial. The essence of overfitting is to unknowingly extract some of the residual variation (i.e., noise) as if that variation represents the underlying model structure.
Underfitting occurs when a mathematical model cannot adequately capture the underlying structure of the data. An under-fitted model is a model that is missing some parameters or terms that would appear in a correctly specified model. Underfitting would occur, for example, when fitting a linear model to nonlinear data. Such a model will tend to have poor predictive performance.
The possibility of over-fitting exists when the criterion used for selecting the model is not the same as the criterion used to judge the suitability of a model. For example, a model might be selected by maximizing its performance on some set of training data, yet its suitability might be determined by its ability to perform well on unseen data; overfitting occurs when a model begins to "memorize" training data rather than "learning" to generalize from a trend.
As an extreme example, if the number of parameters is the same as or greater than the number of observations, then a model can perfectly predict the training data simply by memorizing the data in its entirety. (For an illustration, see Figure 2.) Such a model will typically fail severely when making predictions.
Overfitting is related to both the complexity of the chosen model and how well it is optimized during training. A function class that is too large, in a suitable sense, relative to the dataset size is likely to overfit. Even when the fitted model does not have an excessive number of parameters, it is to be expected that the fitted relationship will appear to perform less well on a new dataset than on the dataset used for fitting (a phenomenon sometimes known as shrinkage). In particular, the value of the coefficient of determination will shrink relative to the original data.
To lessen the chance or amount of overfitting, several techniques are available (e.g., model comparison, cross-validation, regularization, early stopping, pruning, Bayesian priors, or dropout). The basis of some techniques is to either (1) explicitly penalize overly complex models or (2) test the model's ability to generalize by evaluating its performance on a set of data not used for training, which is assumed to approximate the typical unseen data that a model will encounter.

## Import Policy

This card imports the Wikipedia article summary, not the full article text.
Wikipedia content is licensed under CC BY-SA; use the source URL for full
attribution and further review before promoting article content into reviewed
project knowledge.

## Import Status

Imported as background reference. Not a peer-reviewed source.
