import math
from collections import Counter
from datetime import date, timedelta


def moving_average(values, window):
    if window <= 0:
        raise ValueError("window phai lon hon 0")
    result = []
    for i in range(len(values) - window + 1):
        chunk = values[i:i + window]
        result.append(sum(chunk) / window)
    return result


def normalize_scores(scores):
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if lo == hi:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


def word_frequency(text, top_n=5):
    words = [w.strip(".,;:!?").lower() for w in text.split()]
    words = [w for w in words if w]
    return Counter(words).most_common(top_n)


def binary_search(items, target):
    left, right = 0, len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def fibonacci(n, memo=None):
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]


def transpose(matrix):
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


def days_until(target_date, today=None):
    today = today or date.today()
    return (target_date - today).days


def next_business_day(start):
    current = start + timedelta(days=1)
    while current.weekday() >= 5:
        current += timedelta(days=1)
    return current


def split_into_batches(items, size):
    if size <= 0:
        raise ValueError("size phai lon hon 0")
    return [items[i:i + size] for i in range(0, len(items), size)]


def compute_statistics(values):
    if not values:
        return {"mean": 0.0, "median": 0.0, "std": 0.0}
    ordered = sorted(values)
    n = len(ordered)
    mean = sum(ordered) / n
    mid = n // 2
    median = ordered[mid] if n % 2 else (ordered[mid - 1] + ordered[mid]) / 2
    variance = sum((v - mean) ** 2 for v in ordered) / n
    return {"mean": mean, "median": median, "std": math.sqrt(variance)}


def format_duration(seconds):
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def is_palindrome(text):
    cleaned = [c.lower() for c in text if c.isalnum()]
    return cleaned == cleaned[::-1]


def merge_sorted(a, b):
    result, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result