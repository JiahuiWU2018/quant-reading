"""Common evaluation metrics used across reproductions."""
import numpy as np


def mse(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    return float(np.mean((y_pred - y_true) ** 2))


def mae(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    return float(np.mean(np.abs(y_pred - y_true)))


def mape(y_pred: np.ndarray, y_true: np.ndarray, eps: float = 1e-8) -> float:
    return float(np.mean(np.abs((y_pred - y_true) / (np.abs(y_true) + eps))) * 100)
