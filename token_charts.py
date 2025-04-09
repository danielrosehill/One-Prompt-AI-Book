#!/usr/bin/env python3
"""
Token Chart Generator for Gemini 2.5 Max Output Tokens Test

This script creates simple charts focusing on token data from the project.
It generates basic visualizations that can be embedded directly in the README.md file.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from token_estimator import estimate_tokens_for_file, MAX_TOKENS

# Set style for plots
plt.style.use('ggplot')

# Define file paths
FILE_PATHS = {
    'ai_studio': 'book/gemini/via-ai-studio/output1.md',
    'script': 'book/gemini/via-script/output_20250409_225904.md',
    'anthropic': 'book/anthropic/output1.md'
}

# Define output directory for visualizations
OUTPUT_DIR = 'charts'
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def create_token_count_chart(token_data, output_path):
    """
    Create a bar chart comparing token counts.
    
    Args:
        token_data (dict): Dictionary containing the token data
        output_path (str): Path to save the chart
    """
    plt.figure(figsize=(12, 7))
    
    # Data for chart
    sources = ['AI Studio', 'Script', 'Anthropic']
    token_counts = [
        token_data['ai_studio']['original_token_count'], 
        token_data['script']['original_token_count'],
        token_data['anthropic']['original_token_count']
    ]
    
    # Create bar chart with different colors
    bars = plt.bar(sources, token_counts, color=['#4285F4', '#34A853', '#EA4335'])
    
    # Add max token reference line
    plt.axhline(y=MAX_TOKENS, color='#FBBC05', linestyle='-', 
                label=f'Max Tokens: {MAX_TOKENS:,}')
    
    # Add labels and title
    plt.xlabel('Source')
    plt.ylabel('Token Count')
    plt.title('Token Count Comparison: AI Studio vs Script vs Anthropic')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 2000,
                f'{int(height):,}',
                ha='center', va='bottom', fontweight='bold')
    
    # Add percentage labels
    for i, bar in enumerate(bars):
        height = bar.get_height()
        percentage = (height / MAX_TOKENS) * 100
        plt.text(bar.get_x() + bar.get_width()/2., height/2,
                f'{percentage:.1f}%\nof max',
                ha='center', va='center', color='white', fontweight='bold')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_percentage_chart(token_data, output_path):
    """
    Create a pie chart showing the percentage of max tokens used.
    
    Args:
        token_data (dict): Dictionary containing the token data
        output_path (str): Path to save the chart
    """
    plt.figure(figsize=(12, 8))
    
    # Data for chart
    ai_studio_tokens = token_data['ai_studio']['original_token_count']
    script_tokens = token_data['script']['original_token_count']
    anthropic_tokens = token_data['anthropic']['original_token_count']
    
    # Find the maximum tokens used to calculate remaining
    max_tokens_used = max(ai_studio_tokens, script_tokens, anthropic_tokens)
    remaining_tokens = MAX_TOKENS - max_tokens_used
    
    # Create pie chart
    labels = ['AI Studio', 'Script', 'Anthropic', 'Unused Capacity']
    sizes = [ai_studio_tokens, script_tokens, anthropic_tokens, remaining_tokens]
    colors = ['#4285F4', '#34A853', '#EA4335', '#EEEEEE']
    explode = (0.1, 0.1, 0.1, 0)  # explode all model slices
    
    # Create the pie chart
    patches, texts, autotexts = plt.pie(sizes, explode=explode, labels=labels, 
                                       colors=colors, autopct='%1.1f%%',
                                       shadow=True, startangle=140)
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis('equal')
    plt.title('Percentage of Maximum Token Capacity (65,536 tokens) Used')
    
    # Add a legend with token counts
    ai_studio_percent = (ai_studio_tokens / MAX_TOKENS) * 100
    script_percent = (script_tokens / MAX_TOKENS) * 100
    anthropic_percent = (anthropic_tokens / MAX_TOKENS) * 100
    unused_percent = (remaining_tokens / MAX_TOKENS) * 100
    
    legend_labels = [
        f'AI Studio: {ai_studio_tokens:,} tokens ({ai_studio_percent:.1f}%)',
        f'Script: {script_tokens:,} tokens ({script_percent:.1f}%)',
        f'Anthropic: {anthropic_tokens:,} tokens ({anthropic_percent:.1f}%)',
        f'Unused Capacity: {remaining_tokens:,} tokens ({unused_percent:.1f}%)'
    ]
    plt.legend(legend_labels, loc="best")
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_comparison_bar(token_data, output_path):
    """
    Create a comparison bar chart showing token and word counts.
    
    Args:
        token_data (dict): Dictionary containing the token data
        output_path (str): Path to save the chart
    """
    plt.figure(figsize=(14, 8))
    
    # Data preparation
    sources = ['AI Studio', 'Script', 'Anthropic']
    token_counts = [
        token_data['ai_studio']['original_token_count'],
        token_data['script']['original_token_count'],
        token_data['anthropic']['original_token_count']
    ]
    word_counts = [
        token_data['ai_studio']['word_count'],
        token_data['script']['word_count'],
        token_data['anthropic']['word_count']
    ]
    
    # Set up bar positions
    x = np.arange(len(sources))
    width = 0.35
    
    # Create bars
    plt.bar(x - width/2, word_counts, width, label='Words', color='#4285F4')
    plt.bar(x + width/2, token_counts, width, label='Tokens', color='#34A853')
    
    # Customize chart
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.title('Word Count vs Token Count Comparison')
    plt.xticks(x, sources)
    plt.legend()
    
    # Add value labels
    for i, v in enumerate(word_counts):
        plt.text(i - width/2, v, f'{v:,}', ha='center', va='bottom')
    for i, v in enumerate(token_counts):
        plt.text(i + width/2, v, f'{v:,}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_token_to_word_ratio_chart(token_data, output_path):
    """
    Create a bar chart comparing token-to-word ratios.
    
    Args:
        token_data (dict): Dictionary containing the token data
        output_path (str): Path to save the chart
    """
    plt.figure(figsize=(10, 6))
    
    # Data for chart
    sources = ['AI Studio', 'Script', 'Anthropic']
    ratios = [
        token_data['ai_studio']['token_to_word_ratio'],
        token_data['script']['token_to_word_ratio'],
        token_data['anthropic']['token_to_word_ratio']
    ]
    
    # Create bar chart
    bars = plt.bar(sources, ratios, color=['#4285F4', '#34A853', '#EA4335'])
    
    # Add labels and title
    plt.xlabel('Source')
    plt.ylabel('Token-to-Word Ratio')
    plt.title('Token-to-Word Ratio Comparison')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{height:.2f}',
                ha='center', va='bottom', fontweight='bold')
    
    # Set y-axis to start at 0
    plt.ylim(0, max(ratios) + 0.2)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_book_comparison_chart(token_data, output_path):
    """
    Create a bar chart comparing output word counts with classic books.
    
    Args:
        token_data (dict): Dictionary containing the token data
        output_path (str): Path to save the chart
    """
    plt.figure(figsize=(14, 8))
    
    # Data for chart
    books = [
        'Sherlock\nHolmes', 
        'Dorian\nGray', 
        'Pride &\nPrejudice', 
        'Frankenstein',
        'AI Studio\nOutput',
        'Script\nOutput',
        'Anthropic\nOutput'
    ]
    
    word_counts = [
        46500,  # Sherlock Holmes
        78000,  # Dorian Gray
        120000, # Pride & Prejudice
        78000,  # Frankenstein
        token_data['ai_studio']['word_count'],
        token_data['script']['word_count'],
        token_data['anthropic']['word_count']
    ]
    
    # Create color list (gray for books, colored for outputs)
    colors = ['#AAAAAA', '#AAAAAA', '#AAAAAA', '#AAAAAA', '#4285F4', '#34A853', '#EA4335']
    
    # Create bar chart
    bars = plt.bar(books, word_counts, color=colors)
    
    # Add labels and title
    plt.xlabel('Book/Output')
    plt.ylabel('Word Count')
    plt.title('Word Count Comparison: Classic Books vs. AI Outputs')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 2000,
                f'{int(height):,}',
                ha='center', va='bottom')
    
    # Add a reference line for the claimed maximum word count (48,750)
    plt.axhline(y=48750, color='#FBBC05', linestyle='-', 
                label='Claimed Max Words: 48,750')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

if __name__ == "__main__":
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get token data
    token_data = get_token_data()
    
    # Generate charts
    create_token_count_chart(token_data, os.path.join(OUTPUT_DIR, 'token_counts.png'))
    create_percentage_chart(token_data, os.path.join(OUTPUT_DIR, 'token_percentage.png'))
    create_comparison_bar(token_data, os.path.join(OUTPUT_DIR, 'word_token_comparison.png'))
    create_token_to_word_ratio_chart(token_data, os.path.join(OUTPUT_DIR, 'token_to_word_ratio.png'))
    create_book_comparison_chart(token_data, os.path.join(OUTPUT_DIR, 'book_comparison.png'))
