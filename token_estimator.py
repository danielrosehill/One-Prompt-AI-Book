#!/usr/bin/env python3
"""
Token Estimator Script for Gemini 2.5 Max Output Tokens Test

This script estimates the number of tokens in markdown files using tiktoken,
which provides a reasonable approximation for LLM tokenization.

It supports both the AI Studio and script output files and provides:
1. Token count estimates
2. Comparison with the claimed maximum (65,536 tokens)
3. Comparison with the word count
"""

import os
import re
import tiktoken
import argparse
from pathlib import Path

# Define file paths (same as in improved_word_counter.py)
DEFAULT_FILES = {
    'ai_studio': 'book/ai-studio/output1.md',
    'script': 'book/from-script/output_20250409_225904.md'
}

# Claimed maximum tokens for Gemini 2.5
MAX_TOKENS = 65536

def count_tokens(text, model="cl100k_base"):
    """
    Count the number of tokens in a text using tiktoken.
    
    Args:
        text (str): The text to count tokens for
        model (str): The encoding model to use (default: cl100k_base which is similar to GPT-4)
    
    Returns:
        int: The number of tokens
    """
    try:
        encoding = tiktoken.get_encoding(model)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0

def clean_markdown(content):
    """
    Clean markdown content for more accurate token counting.
    Similar to the cleaning in improved_word_counter.py.
    
    Args:
        content (str): The markdown content
    
    Returns:
        str: Cleaned content
    """
    # Remove code blocks
    cleaned = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    # Remove markdown headers but keep the text
    cleaned = re.sub(r'^#+\s+', '', cleaned, flags=re.MULTILINE)
    
    # Remove markdown formatting but keep the text
    cleaned = re.sub(r'\*\*|\*|__|\||---|>', '', cleaned)
    
    # Remove HTML tags but keep the content
    cleaned = re.sub(r'<[^>]*>', '', cleaned)
    
    return cleaned

def estimate_tokens_for_file(file_path, clean=True):
    """
    Estimate tokens for a file.
    
    Args:
        file_path (str): Path to the file
        clean (bool): Whether to clean markdown before counting
    
    Returns:
        dict: Token statistics
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Count words (similar to improved_word_counter.py)
            words = re.findall(r'\b\w+\b', content)
            word_count = len(words)
            
            # Count tokens in original content
            original_token_count = count_tokens(content)
            
            # Count tokens in cleaned content if requested
            cleaned_token_count = None
            if clean:
                cleaned_content = clean_markdown(content)
                cleaned_token_count = count_tokens(cleaned_content)
            
            # Calculate token-to-word ratio
            token_to_word_ratio = original_token_count / word_count if word_count > 0 else 0
            
            # Check for claimed word count in the script output
            claimed_count = None
            for line in content.split('\n'):
                if "Manuscript Word Count" in line:
                    match = re.search(r'Approximately ([0-9,]+)', line)
                    if match:
                        claimed_count = int(match.group(1).replace(',', ''))
            
            return {
                'file_path': file_path,
                'word_count': word_count,
                'original_token_count': original_token_count,
                'cleaned_token_count': cleaned_token_count,
                'token_to_word_ratio': token_to_word_ratio,
                'percentage_of_max': (original_token_count / MAX_TOKENS) * 100,
                'claimed_word_count': claimed_count
            }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def estimate_tokens_range(word_count, min_ratio=0.7, max_ratio=1.4):
    """
    Estimate a range of tokens based on word count.
    
    Args:
        word_count (int): The word count
        min_ratio (float): Minimum token-to-word ratio
        max_ratio (float): Maximum token-to-word ratio
    
    Returns:
        tuple: (min_tokens, max_tokens)
    """
    min_tokens = int(word_count * min_ratio)
    max_tokens = int(word_count * max_ratio)
    return (min_tokens, max_tokens)

def main():
    parser = argparse.ArgumentParser(description='Estimate tokens in markdown files')
    parser.add_argument('--file', help='Path to a specific file to analyze')
    parser.add_argument('--no-clean', action='store_true', help='Skip markdown cleaning')
    args = parser.parse_args()
    
    files_to_process = {}
    
    if args.file:
        # Process a single file if specified
        file_path = args.file
        file_name = os.path.basename(file_path)
        files_to_process[file_name] = file_path
    else:
        # Process default files
        files_to_process = DEFAULT_FILES
    
    print("TOKEN ESTIMATION ANALYSIS:")
    print("-" * 80)
    
    results = {}
    
    for name, file_path in files_to_process.items():
        print(f"\nAnalyzing {name} ({file_path}):")
        stats = estimate_tokens_for_file(file_path, clean=not args.no_clean)
        
        if stats:
            results[name] = stats
            
            print(f"  - Word count: {stats['word_count']:,}")
            print(f"  - Token count (original): {stats['original_token_count']:,}")
            
            if stats['cleaned_token_count'] is not None:
                print(f"  - Token count (cleaned markdown): {stats['cleaned_token_count']:,}")
            
            print(f"  - Token-to-word ratio: {stats['token_to_word_ratio']:.2f}")
            print(f"  - Percentage of max tokens (65,536): {stats['percentage_of_max']:.2f}%")
            
            # Show claimed word count if available
            if stats['claimed_word_count']:
                print(f"  - Claimed word count: {stats['claimed_word_count']:,}")
                
                # Estimate tokens for claimed word count
                min_tokens, max_tokens = estimate_tokens_range(stats['claimed_word_count'])
                print(f"  - Estimated tokens for claimed word count: {min_tokens:,} - {max_tokens:,}")
                print(f"  - Estimated percentage of max: {(min_tokens / MAX_TOKENS * 100):.2f}% - {(max_tokens / MAX_TOKENS * 100):.2f}%")
    
    # Print summary if we have both results
    if len(results) >= 2 and 'ai_studio' in results and 'script' in results:
        ai_studio = results['ai_studio']
        script = results['script']
        
        print("\nSUMMARY COMPARISON:")
        print("-" * 80)
        print(f"{'Metric':<30} {'AI Studio':<15} {'Script':<15}")
        print("-" * 80)
        print(f"{'Word count':<30} {ai_studio['word_count']:,} {script['word_count']:,}")
        print(f"{'Token count':<30} {ai_studio['original_token_count']:,} {script['original_token_count']:,}")
        print(f"{'Token-to-word ratio':<30} {ai_studio['token_to_word_ratio']:.2f} {script['token_to_word_ratio']:.2f}")
        print(f"{'Percentage of max tokens':<30} {ai_studio['percentage_of_max']:.2f}% {script['percentage_of_max']:.2f}%")
        
        # Calculate difference
        token_diff = script['original_token_count'] - ai_studio['original_token_count']
        token_diff_percent = (token_diff / ai_studio['original_token_count']) * 100
        print(f"{'Token count difference':<30} {token_diff:,} ({token_diff_percent:+.2f}%)")

if __name__ == "__main__":
    main()