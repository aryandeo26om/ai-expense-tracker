from sklearn.linear_model import LinearRegression
import numpy as np

def predict_expense(data):
    if len(data) < 2:
        return 0

    X = np.array(range(len(data))).reshape(-1, 1)
    y = np.array([row[3] for row in data])

    model = LinearRegression()
    model.fit(X, y)

    return model.predict([[len(data)]])[0]