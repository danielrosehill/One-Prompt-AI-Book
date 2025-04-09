#!/usr/bin/env python3
"""
Updated Analysis Script for Gemini 2.5 Max Output Tokens Test

This script calculates the percentage of words achieved compared to the 40,000 word target
and finds public domain books with similar word counts to the AI outputs for comparison.
"""

import os
import re
import matplotlib.pyplot as plt
from token_estimator import estimate_tokens_for_file

# Define file paths
FILE_PATHS = {
    'ai_studio': 'book/gemini/via-ai-studio/output1.md',
    'script': 'book/gemini/via-script/output_20250409_225904.md',
    'anthropic': 'book/anthropic/output1.md'
}

# Define output directory for visualizations
OUTPUT_DIR = 'charts'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Target word count from the prompt
TARGET_WORD_COUNT = 40000

# Public domain books with word counts (for comparison)
BOOKS = [
    {"title": "The Adventures of Sherlock Holmes", "author": "Arthur Conan Doyle", "word_count": 46500},
    {"title": "The Picture of Dorian Gray", "author": "Oscar Wilde", "word_count": 78000},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "word_count": 120000},
    {"title": "Frankenstein", "author": "Mary Shelley", "word_count": 78000},
    {"title": "The Scarlet Letter", "author": "Nathaniel Hawthorne", "word_count": 63000},
    {"title": "A Christmas Carol", "author": "Charles Dickens", "word_count": 28500},
    {"title": "The Call of the Wild", "author": "Jack London", "word_count": 32000},
    {"title": "Heart of Darkness", "author": "Joseph Conrad", "word_count": 38000},
    {"title": "The Strange Case of Dr. Jekyll and Mr. Hyde", "author": "Robert Louis Stevenson", "word_count": 25500},
    {"title": "The Time Machine", "author": "H.G. Wells", "word_count": 32000},
    {"title": "Ethan Frome", "author": "Edith Wharton", "word_count": 30000},
    {"title": "The Awakening", "author": "Kate Chopin", "word_count": 28000},
]

def get_token_data():
    """
    Collect token data from the token estimator script.
    
    Returns:
        dict: Dictionary containing the token data
    """
    # Get token data
    token_data = {}
    for name, path in FILE_PATHS.items():
        token_data[name] = estimate_tokens_for_file(path)
    
    return token_data

def find_closest_book(word_count):
    """
    Find the book with the closest word count to the given count.
    
    Args:
        word_count (int): The word count to compare against
    
    Returns:
        dict: The book with the closest word count
    """
    closest_book = None
    min_difference = float('inf')
    
    for book in BOOKS:
        difference = abs(book["word_count"] - word_count)
        if difference < min_difference:
            min_difference = difference
            closest_book = book
    
    return closest_book

def create_target_percentage_chart(token_data, output_path):
    """
    Create a bar chart showing percentage of target word count achieved.
    
    Args:
        token_data (dict): Dictionary containing the token data
        output_path (str): Path to save the chart
    """
    plt.figure(figsize=(12, 7))
    
    # Data for chart
    sources = ['AI Studio', 'Script', 'Anthropic']
    word_counts = [
        token_data['ai_studio']['word_count'], 
        token_data['script']['word_count'],
        token_data['anthropic']['word_count']
    ]
    
    # Calculate percentages of target
    percentages = [(count / TARGET_WORD_COUNT) * 100 for count in word_counts]
    
    # Create bar chart with different colors
    bars = plt.bar(sources, percentages, color=['#4285F4', '#34A853', '#EA4335'])
    
    # Add 100% reference line
    plt.axhline(y=100, color='#FBBC05', linestyle='-', 
                label=f'Target: {TARGET_WORD_COUNT:,} words')
    
    # Add labels and title
    plt.xlabel('Source')
    plt.ylabel('Percentage of Target (%)')
    plt.title(f'Percentage of Target Word Count ({TARGET_WORD_COUNT:,} words) Achieved')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.1f}%\n({word_counts[i]:,} words)',
                ha='center', va='bottom', fontweight='bold')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_book_comparison_chart(token_data, output_path):
    """
    Create a bar chart comparing AI outputs with similar public domain books.
    
    Args:
        token_data (dict): Dictionary containing the token data
        output_path (str): Path to save the chart
    """
    plt.figure(figsize=(14, 8))
    
    # Find closest books for each output
    ai_studio_closest = find_closest_book(token_data['ai_studio']['word_count'])
    script_closest = find_closest_book(token_data['script']['word_count'])
    anthropic_closest = find_closest_book(token_data['anthropic']['word_count'])
    
    # Data for chart
    labels = [
        f"AI Studio\n({token_data['ai_studio']['word_count']:,})",
        f"{ai_studio_closest['title']}\n({ai_studio_closest['word_count']:,})",
        f"Script\n({token_data['script']['word_count']:,})",
        f"{script_closest['title']}\n({script_closest['word_count']:,})",
        f"Anthropic\n({token_data['anthropic']['word_count']:,})",
        f"{anthropic_closest['title']}\n({anthropic_closest['word_count']:,})"
    ]
    
    word_counts = [
        token_data['ai_studio']['word_count'],
        ai_studio_closest['word_count'],
        token_data['script']['word_count'],
        script_closest['word_count'],
        token_data['anthropic']['word_count'],
        anthropic_closest['word_count']
    ]
    
    # Create color list (blue for AI Studio, green for script, red for Anthropic, gray for books)
    colors = ['#4285F4', '#AAAAAA', '#34A853', '#AAAAAA', '#EA4335', '#AAAAAA']
    
    # Create bar chart
    bars = plt.bar(labels, word_counts, color=colors)
    
    # Add labels and title
    plt.xlabel('Output / Book')
    plt.ylabel('Word Count')
    plt.title('Word Count Comparison: AI Outputs vs. Similar Public Domain Books')
    
    # Add a reference line for the target word count
    plt.axhline(y=TARGET_WORD_COUNT, color='#FBBC05', linestyle='-', 
                label=f'Target Word Count: {TARGET_WORD_COUNT:,}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    """Main function to run the analysis"""
    print("UPDATED ANALYSIS:")
    print("-" * 80)
    
    # Get token data
    token_data = get_token_data()
    
    # Print percentage of target achieved
    print(f"Target Word Count: {TARGET_WORD_COUNT:,}")
    print("\nPercentage of Target Achieved:")
    print("-" * 80)
    
    for name, data in token_data.items():
        percentage = (data['word_count'] / TARGET_WORD_COUNT) * 100
        print(f"{name.title()}: {data['word_count']:,} words ({percentage:.2f}%)")
    
    # Find closest books for comparison
    print("\nSimilar Public Domain Books:")
    print("-" * 80)
    
    for name, data in token_data.items():
        closest_book = find_closest_book(data['word_count'])
        difference = abs(closest_book['word_count'] - data['word_count'])
        difference_percent = (difference / data['word_count']) * 100
        
        print(f"{name.title()} ({data['word_count']:,} words):")
        print(f"  - Closest book: {closest_book['title']} by {closest_book['author']}")
        print(f"  - Word count: {closest_book['word_count']:,} words")
        print(f"  - Difference: {difference:,} words ({difference_percent:.2f}%)")
    
    # Generate charts
    create_target_percentage_chart(token_data, os.path.join(OUTPUT_DIR, 'target_percentage.png'))
    create_book_comparison_chart(token_data, os.path.join(OUTPUT_DIR, 'similar_books_comparison.png'))
    
    print("\nCharts generated:")
    print(f"  - {os.path.join(OUTPUT_DIR, 'target_percentage.png')}")
    print(f"  - {os.path.join(OUTPUT_DIR, 'similar_books_comparison.png')}")

if __name__ == "__main__":
    main()
