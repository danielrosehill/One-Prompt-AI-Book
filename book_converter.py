#!/usr/bin/env python3
"""
Book Converter Script

This script converts a Markdown file to both EPUB and PDF formats.
The PDF is formatted with a title, table of contents, page numbers in the footer,
and uses the Lato font.
"""

import os
import re
import argparse
import subprocess
import tempfile

def ensure_dependencies():
    """Check and install required dependencies."""
    try:
        # Check if pandoc is installed
        subprocess.run(['pandoc', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Pandoc is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("❌ Pandoc is not installed. Please install it from https://pandoc.org/installing.html")
        return False
    
    # Check if wkhtmltopdf is installed (alternative for PDF generation)
    try:
        subprocess.run(['wkhtmltopdf', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ wkhtmltopdf is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ wkhtmltopdf is not installed. Will try alternative PDF generation methods.")
    
    # Check for Lato font
    try:
        # This command works on most Linux systems
        font_check = subprocess.run(['fc-list', '|', 'grep', '-i', 'lato'], 
                                   shell=True, check=False, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        if not font_check.stdout:
            print("⚠️ Lato font may not be installed. The script will attempt to download it.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ Could not check for Lato font. The script will attempt to download it.")
    
    return True

def download_lato_font():
    """Download Lato font if not already installed."""
    font_dir = os.path.expanduser("~/.local/share/fonts/")
    os.makedirs(font_dir, exist_ok=True)
    
    # URLs for Lato font files
    lato_urls = {
        "Lato-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf",
        "Lato-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Bold.ttf",
        "Lato-Italic.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Italic.ttf",
        "Lato-BoldItalic.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-BoldItalic.ttf"
    }
    
    for font_file, url in lato_urls.items():
        font_path = os.path.join(font_dir, font_file)
        if not os.path.exists(font_path):
            try:
                print(f"Downloading {font_file}...")
                subprocess.run(['wget', url, '-O', font_path], check=True)
            except subprocess.SubprocessError:
                print(f"Failed to download {font_file}. PDF may not use Lato font.")
    
    # Update font cache
    try:
        subprocess.run(['fc-cache', '-f'], check=True)
        print("Font cache updated.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Could not update font cache. You may need to restart your system for fonts to be recognized.")

def extract_title_from_markdown(markdown_file):
    """Extract title and subtitle from the markdown file."""
    title = "The Jerusalem Odyssey"
    subtitle = "A Whimsical Journey of Faith, Friendship, and Talking Sloths"
    
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for title pattern
        title_match = re.search(r'# Title: (.*?)(?:\n|$)', content)
        if title_match:
            title = title_match.group(1).strip()
        
        # Look for subtitle pattern
        subtitle_match = re.search(r'## Subtitle: (.*?)(?:\n|$)', content)
        if subtitle_match:
            subtitle = subtitle_match.group(1).strip()
    
    except Exception as e:
        print(f"Warning: Could not extract title from markdown: {e}")
    
    return title, subtitle

def convert_to_epub(markdown_file, output_file):
    """Convert markdown to EPUB format."""
    title, subtitle = extract_title_from_markdown(markdown_file)
    
    cmd = [
        'pandoc',
        markdown_file,
        '-o', output_file,
        '--epub-cover-image=cover.png',  # Will be created if it doesn't exist
        f'--metadata=title:{title}',
        f'--metadata=subtitle:{subtitle}',
        '--toc',
        '--toc-depth=2',
        '--epub-chapter-level=1'
    ]
    
    # Create a simple cover if it doesn't exist
    if not os.path.exists('cover.png'):
        try:
            create_cover_image(title, subtitle, 'cover.png')
        except Exception as e:
            print(f"Warning: Could not create cover image: {e}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ EPUB created successfully: {output_file}")
        return True
    except subprocess.SubprocessError as e:
        print(f"❌ Failed to create EPUB: {e}")
        return False

def create_cover_image(title, subtitle, output_file):
    """Create a simple cover image using Python's PIL library."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a blank image with a gradient background
        width, height = 1600, 2400
        img = Image.new('RGB', (width, height), color=(240, 240, 245))
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("Lato-Bold.ttf", 120)
            subtitle_font = ImageFont.truetype("Lato-Regular.ttf", 80)
        except IOError:
            # Use default font if Lato is not available
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw title
        title_width = draw.textlength(title, font=title_font)
        draw.text(
            ((width - title_width) / 2, height / 3),
            title,
            font=title_font,
            fill=(0, 0, 0)
        )
        
        # Draw subtitle
        subtitle_width = draw.textlength(subtitle, font=subtitle_font)
        draw.text(
            ((width - subtitle_width) / 2, height / 2),
            subtitle,
            font=subtitle_font,
            fill=(60, 60, 60)
        )
        
        # Save the image
        img.save(output_file)
        print(f"✅ Cover image created: {output_file}")
    except ImportError:
        print("⚠️ PIL/Pillow library not found. Cover image not created.")
        # Create a simple colored rectangle as a fallback
        try:
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(8, 12))
            plt.text(0.5, 0.6, title, fontsize=24, ha='center')
            plt.text(0.5, 0.5, subtitle, fontsize=16, ha='center')
            plt.axis('off')
            plt.savefig(output_file, dpi=200, bbox_inches='tight')
            plt.close()
            print(f"✅ Simple cover image created with matplotlib: {output_file}")
        except ImportError:
            print("❌ Neither PIL nor matplotlib available. No cover image created.")

def convert_to_pdf(markdown_file, output_file):
    """Convert markdown to PDF with specific formatting."""
    title, subtitle = extract_title_from_markdown(markdown_file)
    
    # Create a simple HTML version with CSS for styling
    html_temp = os.path.join(tempfile.gettempdir(), "temp_book.html")
    
    # Create a CSS file for styling
    css_content = """
    body {
        font-family: 'Lato', 'Arial', sans-serif;
        line-height: 1.6;
        max-width: 800px;
        margin: 0 auto;
        padding: 2em;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Lato', 'Arial', sans-serif;
        page-break-after: avoid;
        margin-top: 2em;
    }
    h1 {
        font-size: 2.5em;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.3em;
        page-break-before: always;
    }
    h1:first-of-type {
        page-break-before: avoid;
    }
    h2 {
        font-size: 2em;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.3em;
    }
    h3 { font-size: 1.5em; }
    p { margin: 1em 0; }
    a { color: #0366d6; }
    pre {
        background-color: #f6f8fa;
        border-radius: 3px;
        padding: 1em;
        overflow: auto;
    }
    code {
        background-color: #f6f8fa;
        border-radius: 3px;
        padding: 0.2em 0.4em;
    }
    blockquote {
        border-left: 4px solid #ddd;
        padding-left: 1em;
        color: #777;
    }
    img { max-width: 100%; }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 0.5em;
    }
    th { background-color: #f6f8fa; }
    hr { border: 1px solid #eee; }
    
    /* Title page */
    .title { font-size: 3em; text-align: center; margin-top: 30%; }
    .subtitle { font-size: 1.5em; text-align: center; margin-top: 1em; }
    .author { text-align: center; margin-top: 2em; }
    .date { text-align: center; margin-top: 1em; }
    
    /* Table of contents */
    #toc { page-break-after: always; }
    #toc h2 { text-align: center; }
    """
    
    css_file = os.path.join(tempfile.gettempdir(), "book_style.css")
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # First try using Chrome/Chromium headless if available
    try:
        print("Trying Chrome/Chromium headless for PDF generation...")
        
        # First convert markdown to HTML with pandoc
        html_cmd = [
            'pandoc',
            markdown_file,
            '-o', html_temp,
            '--standalone',
            '--toc',
            '--toc-depth=2',
            '--number-sections',
            f'--metadata=title:{title}',
            f'--css={css_file}'
        ]
        subprocess.run(html_cmd, check=True)
        
        # Try to find Chrome or Chromium
        chrome_paths = [
            'google-chrome',
            'chromium',
            'chromium-browser',
            '/usr/bin/google-chrome',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]
        
        chrome_cmd = None
        for path in chrome_paths:
            try:
                subprocess.run([path, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                chrome_cmd = path
                break
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        if chrome_cmd:
            print(f"Using {chrome_cmd} for PDF generation")
            pdf_cmd = [
                chrome_cmd,
                '--headless',
                '--disable-gpu',
                '--print-to-pdf=' + output_file,
                '--no-margins',
                html_temp
            ]
            subprocess.run(pdf_cmd, check=True)
            print(f"✅ PDF created successfully using Chrome/Chromium: {output_file}")
            return True
        else:
            print("Chrome/Chromium not found.")
            raise FileNotFoundError("Chrome/Chromium not found")
    
    except Exception as e:
        print(f"⚠️ Chrome/Chromium method failed: {e}")
        
        # Try using pandoc with basic options
        try:
            print("Trying basic pandoc PDF conversion...")
            
            # Create a simple standalone HTML file with embedded CSS
            with open(html_temp, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Add page numbers with JavaScript
            html_with_page_numbers = html_content.replace('</body>',
                '''
                <script>
                    window.onload = function() {
                        // Add page numbers in the footer
                        var style = document.createElement('style');
                        style.innerHTML = `
                            @media print {
                                @page { margin: 2cm; }
                                body::after {
                                    content: counter(page);
                                    position: fixed;
                                    bottom: 1cm;
                                    right: 1cm;
                                    font-size: 10pt;
                                }
                            }
                        `;
                        document.head.appendChild(style);
                    };
                </script>
                </body>''')
            
            with open(html_temp, 'w', encoding='utf-8') as f:
                f.write(html_with_page_numbers)
            
            # Try using wkhtmltopdf with minimal options
            try:
                simple_pdf_cmd = [
                    'wkhtmltopdf',
                    '--page-size', 'A4',
                    html_temp, output_file
                ]
                subprocess.run(simple_pdf_cmd, check=True)
                print(f"✅ PDF created with wkhtmltopdf basic options: {output_file}")
                return True
            except subprocess.SubprocessError:
                # Last resort - try direct pandoc to PDF without specific engine
                basic_cmd = [
                    'pandoc',
                    markdown_file,
                    '-o', output_file,
                    '--from=markdown',
                    '--standalone'
                ]
                subprocess.run(basic_cmd, check=True)
                print(f"✅ PDF created with basic pandoc: {output_file}")
                return True
        
        except subprocess.SubprocessError as e2:
            print(f"❌ All PDF conversion methods failed: {e2}")
            
            # Create a simple text version as a last resort
            try:
                print("Creating a plain text version as fallback...")
                txt_output = os.path.splitext(output_file)[0] + ".txt"
                txt_cmd = [
                    'pandoc',
                    markdown_file,
                    '-o', txt_output,
                    '--from=markdown',
                    '--to=plain'
                ]
                subprocess.run(txt_cmd, check=True)
                print(f"✅ Plain text version created: {txt_output}")
                return False
            except:
                print("❌ Even plain text conversion failed.")
                return False

def main():
    parser = argparse.ArgumentParser(description='Convert Markdown to EPUB and PDF')
    parser.add_argument('input_file', help='Input Markdown file')
    parser.add_argument('--epub-only', action='store_true', help='Generate only EPUB format')
    parser.add_argument('--pdf-only', action='store_true', help='Generate only PDF format')
    parser.add_argument('--output-dir', default='.', help='Output directory')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check dependencies
    if not ensure_dependencies():
        print("Missing required dependencies. Please install them and try again.")
        return 1
    
    # Download Lato font if needed
    download_lato_font()
    
    # Get base filename without extension
    base_name = os.path.splitext(os.path.basename(args.input_file))[0]
    
    # Convert to EPUB if not PDF-only
    if not args.pdf_only:
        epub_output = os.path.join(args.output_dir, f"{base_name}.epub")
        convert_to_epub(args.input_file, epub_output)
    
    # Convert to PDF if not EPUB-only
    if not args.epub_only:
        pdf_output = os.path.join(args.output_dir, f"{base_name}.pdf")
        convert_to_pdf(args.input_file, pdf_output)
    
    return 0

if __name__ == "__main__":
    exit(main())
