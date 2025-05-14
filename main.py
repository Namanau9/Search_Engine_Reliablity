import time
import random
import requests
from typing import List, Dict, Set
import streamlit as st
import pandas as pd

# Replace with your actual SerpAPI key
SERPAPI_API_KEY = "a50fd208b1dbed6c62705fe9f3c55676189edc80d2f3d195994aa898bfd63bb3"

# Real-world API-based search engine fetch using SerpAPI
def fetch_results(query: str) -> Dict[str, List[str]]:
    engines = ["google", "bing", "duckduckgo"]
    results = {}
    for engine in engines:
        url = f"https://serpapi.com/search.json?q={query}&engine={engine}&api_key={SERPAPI_API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
            links = []
            if "organic_results" in data:
                for item in data["organic_results"][:5]:
                    link = item.get("link") or item.get("url")
                    if link:
                        links.append(link)
            results[engine.capitalize()] = links
        except Exception as e:
            results[engine.capitalize()] = [f"Error fetching results: {e}"]
    return results

# Sorting Algorithms
def merge_sort(arr: List[str]) -> List[str]:
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left: List[str], right: List[str]) -> List[str]:
    result = []
    while left and right:
        if left[0] < right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    result.extend(left)
    result.extend(right)
    return result

def quick_sort(arr: List[str]) -> List[str]:
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    less = [x for x in arr[1:] if x < pivot]
    greater = [x for x in arr[1:] if x >= pivot]
    return quick_sort(less) + [pivot] + quick_sort(greater)

def bubble_sort(arr: List[str]) -> List[str]:
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def selection_sort(arr: List[str]) -> List[str]:
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

# Jaccard Similarity
def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    return len(set1 & set2) / len(set1 | set2)

def evaluate_reliability(results: Dict[str, List[str]]) -> Dict[str, float]:
    engines = list(results.keys())
    reliability_scores = {engine: 0.0 for engine in engines}
    for i in range(len(engines)):
        for j in range(i+1, len(engines)):
            set1 = set(results[engines[i]])
            set2 = set(results[engines[j]])
            score = jaccard_similarity(set1, set2)
            reliability_scores[engines[i]] += score
            reliability_scores[engines[j]] += score
    for engine in reliability_scores:
        reliability_scores[engine] /= (len(engines) - 1)
    return reliability_scores

def test_sorting_algorithms(results: List[str]):
    algorithms = {
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
        "Bubble Sort": bubble_sort,
        "Selection Sort": selection_sort
    }
    timings = {}
    for name, func in algorithms.items():
        data = results[:]
        start = time.time()
        sorted_data = func(data)
        end = time.time()
        timings[name] = end - start
    return timings

# Streamlit UI
st.title("Search Engine Reliability Analyzer")
st.write("This tool compares search engine results for a given query using sorting performance and reliability metrics.")

query = st.text_input("Enter Search Query")
if st.button("Analyze") and query:
    with st.spinner("Fetching search engine results..."):
        results = fetch_results(query)

    st.subheader("Search Engine Results")
    for engine, links in results.items():
        st.markdown(f"**{engine}:**")
        for link in links:
            st.markdown(f"- {link}")

    st.subheader("Sorting Performance (Time in seconds)")
    for engine in results:
        if "Error" in results[engine][0]:
            continue
        timings = test_sorting_algorithms(results[engine])
        df = pd.DataFrame(list(timings.items()), columns=["Algorithm", "Time (s)"])
        st.markdown(f"**{engine}**")
        st.bar_chart(df.set_index("Algorithm"))

    st.subheader("Search Engine Reliability Scores")
    reliability = evaluate_reliability(results)
    rel_df = pd.DataFrame(list(reliability.items()), columns=["Engine", "Reliability"])
    st.dataframe(rel_df.set_index("Engine"))
    st.bar_chart(rel_df.set_index("Engine"))
