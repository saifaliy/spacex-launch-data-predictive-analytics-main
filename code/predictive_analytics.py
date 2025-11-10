# Import the required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

# Create a function to plot the confusion matrix
def plot_confusion_matrix(x,y,predict):
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y, predict)
    ax = plt.subplot()
    sns.heatmap(cm, annot=True, fmt='d', ax=ax, cmap='Blues')
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title('Confusion Matrix')
    ax.xaxis.set_ticklabels(['did not land', 'landed'])
    ax.yaxis.set_ticklabels(['did not land', 'landed'])
    plt.show()


# Load the dataset
data = pd.read_csv("dataset_part_2.csv")
data.head()

X = pd.read_csv("dataset_part_3.csv")
X.head()

# Create a NumPy array from the column Class in data
Y = data['Class'].to_numpy()

# Standardize the data in X then reassign it to the variable X
transform = preprocessing.StandardScaler()
X = transform.fit_transform(X) # Very important otherwise data doesn't converge, and coefficients become unstable

# Split the data into training and testing data
X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2, random_state = 2)
Y_test.shape # 18 test samples available

# Create a logistic regression object and GridSearchCV object
parameters1 ={"C":[0.01,0.1,1],'penalty':['l2'], 'solver':['lbfgs']}# l1 lasso l2 ridge
lr=LogisticRegression(max_iter=1000)
logreg_cv = GridSearchCV(estimator=lr, param_grid=parameters1, cv = 10)
logreg_cv.fit(X_train, Y_train)

# Output
print("tuned hpyerparameters :(best parameters) ",logreg_cv.best_params_)
print("accuracy :",logreg_cv.best_score_)

# Calculate the accuracy on the test data
logreg_cv.score(X_test,Y_test)

# Let's look at the confusion matrix
yhat=logreg_cv.predict(X_test)
plot_confusion_matrix(logreg_cv, Y_test,yhat)

# Support vector machine
parameters2 = {'kernel':('linear', 'rbf','poly','rbf', 'sigmoid'),
              'C': np.logspace(-3, 3, 5),
              'gamma':np.logspace(-3, 3, 5)}
svm = SVC()
svm_cv = GridSearchCV(estimator=svm, param_grid=parameters2, cv = 10)
svm_cv.fit(X_train, Y_train)

#Output
print("tuned hpyerparameters :(best parameters) ",svm_cv.best_params_)
print("accuracy :",svm_cv.best_score_)

# Calculate the accuracy on the test data
svm_cv.score(X_test,Y_test)

# Let's look at the confusion matrix now
yhat=svm_cv.predict(X_test)
plot_confusion_matrix(svm_cv, Y_test,yhat)

# Decision Tree
parameters3 = {
    'criterion': ['gini', 'entropy'],
    'splitter': ['best', 'random'],
    'max_depth': [4, 6, 8, 10],                # fewer, meaningful depths
    'max_features': ['sqrt', 'log2', None],    # 'auto' removed
    'min_samples_leaf': [1, 2, 4],
    'min_samples_split': [2, 5, 10]
}
tree = DecisionTreeClassifier(random_state=42)
tree_cv = GridSearchCV(estimator=tree, param_grid=parameters3, cv = 10)
tree_cv.fit(X_train, Y_train)

# Output
print("tuned hpyerparameters :(best parameters) ",tree_cv.best_params_)
print("accuracy :",tree_cv.best_score_)

# Calculate the accuracy on the test data
tree_cv.score(X_test,Y_test)

# Let's look at the confusion matrix now
yhat = tree_cv.predict(X_test)
plot_confusion_matrix(tree_cv, Y_test, yhat)

# K-Nearest Neighbors
parameters4 = {'n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
              'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
              'p': [1,2]}

KNN = KNeighborsClassifier()

knn_cv = GridSearchCV(estimator=KNN, param_grid=parameters4, cv = 10)
knn_cv.fit(X_train, Y_train)

print("tuned hpyerparameters :(best parameters) ",knn_cv.best_params_)
print("accuracy :",knn_cv.best_score_)

knn_cv.score(X_test, Y_test)

yhat = knn_cv.predict(X_test)
plot_confusion_matrix(knn_cv, Y_test,yhat)