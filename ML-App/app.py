#!/usr/bin/env python3
import sys
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression

# Read dataset as the 1st command line argument
if len(sys.argv) < 2:
    print("Error: Please provide the dataset filename as an argument.")
    sys.exit(1)

dataset = sys.argv[1]

# Load dataset
df = pd.read_csv("/work/" + dataset)

# Get X data (features only) and y data (target variable)
X = df.iloc[:, :-1]
y = df.iloc[:, -1]

# Create a Linear Regression object and apply 5-fold cross-validation
lreg = LinearRegression()
scores = cross_val_score(lreg, X, y, cv=5)

# Compute avg score
score = sum(scores) / scores.size

# Write output
with open("/work/" + dataset + ".out", "a") as text_file:
    text_file.write(str(score) + "\n")

print(f"Success! Average CV Score {score} written to /work/{dataset}.out")
