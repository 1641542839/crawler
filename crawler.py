#!/usr/bin/env python3
"""
Web Crawler Script
Recursively crawls websites starting from seed URLs with configurable depth and delay.
Respects robots.txt and saves HTML content and linked files.
"""

import argparse
import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, Tuple, List
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Please install: pip install requests beautifulsoup4")
    sys.exit(1)

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class Crawler:
    """Main crawler class that handles web crawling with configurable options."""
    
    def __init__(self, args):
        """Initialize crawler with command-line arguments."""
        self.args = args
        self.visited_urls: Set[str] = set()
        self.robots_cache: dict = {}  # Cache robots.txt parsers by domain
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': args.user_agent})
        self.pages_crawled = 0
        
        # Create necessary directories
        self.raw_dir = Path('./data/raw')
        self.raw_files_dir = Path('./data/raw_files')
        self.index_file = Path('./data/raw/index.jsonl')
        
        # Progress bar
        self.pbar = None
        if TQDM_AVAILABLE and not args.verbose:
            self.pbar = tqdm(total=args.max_pages, desc="Crawling")
    
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.args.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def read_seeds(self) -> List[str]:
        """Read seed URLs from seeds.txt file, ignoring comments and empty lines."""
        seeds = []
        try:
            with open(self.args.seeds, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        seeds.append(line)
            self.log(f"Loaded {len(seeds)} seed URLs from {self.args.seeds}")
            return seeds
        except FileNotFoundError:
            self.log(f"Seeds file not found: {self.args.seeds}", "ERROR")
            return []
        except Exception as e:
            self.log(f"Error reading seeds file: {e}", "ERROR")
            return []
    
    def get_robots_parser(self, url: str) -> Optional[RobotFileParser]:
        """Get or create a RobotFileParser for the given URL's domain."""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        if base_url in self.robots_cache:
            return self.robots_cache[base_url]
        
        # Create new robots.txt parser
        robots_url = urljoin(base_url, '/robots.txt')
        rp = RobotFileParser()
        rp.set_url(robots_url)
        
        try:
            rp.read()
            self.robots_cache[base_url] = rp
            self.log(f"Loaded robots.txt from {robots_url}")
            return rp
        except Exception as e:
            self.log(f"Could not load robots.txt from {robots_url}: {e}", "WARNING")
            # Cache None to indicate no robots.txt available (allow all)
            self.robots_cache[base_url] = None
            return None
    
    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        rp = self.get_robots_parser(url)
        if rp:
            return rp.can_fetch(self.args.user_agent, url)
        return True  # If no robots.txt, allow fetching
    
    def fetch_page(self, url: str) -> Tuple[Optional[bytes], int, str, int]:
        """
        Fetch a page with retry logic for transient errors.
        
        Returns:
            Tuple of (content, status_code, content_type, content_length)
        """
        for attempt in range(3):  # Retry up to 3 times
            try:
                self.log(f"Fetching URL (attempt {attempt + 1}/3): {url}")
                
                response = self.session.get(
                    url,
                    timeout=30,
                    allow_redirects=True
                )
                
                content_type = response.headers.get('Content-Type', '').lower()
                content_length = len(response.content)
                
                return response.content, response.status_code, content_type, content_length
                
            except requests.exceptions.Timeout:
                self.log(f"Timeout fetching {url} (attempt {attempt + 1}/3)", "WARNING")
                if attempt < 2:  # Don't sleep on last attempt
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.ConnectionError as e:
                self.log(f"Connection error fetching {url}: {e} (attempt {attempt + 1}/3)", "WARNING")
                if attempt < 2:
                    time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                self.log(f"Request error fetching {url}: {e}", "ERROR")
                return None, 0, "", 0
        
        # All retries failed
        self.log(f"Failed to fetch {url} after 3 attempts", "ERROR")
        return None, 0, "", 0
    
    def parse_links(self, html_content: bytes, base_url: str) -> Set[str]:
        """
        Parse HTML content and extract all links.
        
        Args:
            html_content: Raw HTML bytes
            base_url: Base URL for resolving relative links
            
        Returns:
            Set of absolute URLs found in the page
        """
        links = set()
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all anchor tags with href attribute
            for tag in soup.find_all('a', href=True):
                href = tag['href']
                # Resolve relative URLs
                absolute_url = urljoin(base_url, href)
                # Remove fragment
                absolute_url = absolute_url.split('#')[0]
                if absolute_url:
                    links.add(absolute_url)
            
            self.log(f"Found {len(links)} links in {base_url}")
            
        except Exception as e:
            self.log(f"Error parsing links from {base_url}: {e}", "ERROR")
        
        return links
    
    def should_follow(self, url: str, seed_url: str) -> bool:
        """
        Determine if a URL should be followed based on constraints.
        
        Constraints:
        - Same hostname as seed
        - URL path starts with seed path (stay within seed path prefix)
        
        Args:
            url: URL to check
            seed_url: Original seed URL
            
        Returns:
            True if URL should be followed, False otherwise
        """
        url_parsed = urlparse(url)
        seed_parsed = urlparse(seed_url)
        
        # Check same hostname
        if url_parsed.netloc != seed_parsed.netloc:
            return False
        
        # Check path prefix
        url_path = url_parsed.path
        seed_path = seed_parsed.path
        
        # Normalize paths (remove trailing slash for comparison)
        seed_path_prefix = seed_path.rstrip('/')
        
        # If seed path is empty or root, allow any path on same host
        if not seed_path_prefix or seed_path_prefix == '/':
            return True
        
        # Check if URL path starts with seed path prefix
        if not url_path.startswith(seed_path_prefix):
            return False
        
        return True
    
    def save_raw(self, content: bytes, url: str, is_file: bool = False) -> str:
        """
        Save raw content to disk.
        
        Args:
            content: Raw bytes to save
            url: URL of the content (used for generating filename)
            is_file: If True, save to raw_files directory with extension
            
        Returns:
            Path where content was saved
        """
        # Generate SHA1 hash of URL for unique filename
        url_hash = hashlib.sha1(url.encode()).hexdigest()
        
        if is_file:
            # Extract file extension from URL
            parsed = urlparse(url)
            path = parsed.path
            ext = os.path.splitext(path)[1].lower()
            if not ext:
                ext = '.bin'
            
            # Save to raw_files directory
            self.raw_files_dir.mkdir(parents=True, exist_ok=True)
            filepath = self.raw_files_dir / f"{url_hash}{ext}"
        else:
            # Save HTML to date-based directory
            date_str = datetime.now().strftime("%Y%m%d")
            date_dir = self.raw_dir / date_str
            date_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract hostname for filename
            hostname = urlparse(url).netloc.replace(':', '_')
            filepath = date_dir / f"{hostname}_{url_hash}.html"
        
        # Write content
        try:
            with open(filepath, 'wb') as f:
                f.write(content)
            self.log(f"Saved content to {filepath}")
            return str(filepath)
        except Exception as e:
            self.log(f"Error saving content: {e}", "ERROR")
            return ""
    
    def log_metadata(self, url: str, status_code: int, content_type: str, 
                     saved_path: str, depth: int, parent_url: str, content_length: int):
        """Append metadata as JSON line to index.jsonl."""
        metadata = {
            'url': url,
            'status_code': status_code,
            'content_type': content_type,
            'saved_path': saved_path,
            'crawl_date': datetime.now().isoformat(),
            'depth': depth,
            'parent_url': parent_url,
            'content_length': content_length
        }
        
        try:
            # Ensure directory exists
            self.index_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.index_file, 'a') as f:
                f.write(json.dumps(metadata) + '\n')
            self.log(f"Logged metadata for {url}")
        except Exception as e:
            self.log(f"Error logging metadata: {e}", "ERROR")
    
    def crawl_seed(self, seed_url: str):
        """
        Crawl a single seed URL recursively up to max depth.
        
        Args:
            seed_url: Starting URL to crawl
        """
        self.log(f"Starting crawl from seed: {seed_url}")
        
        # Queue: (url, depth, parent_url)
        queue = [(seed_url, 0, "")]
        
        while queue and (self.args.max_pages == 0 or self.pages_crawled < self.args.max_pages):
            url, depth, parent_url = queue.pop(0)
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            # Skip if depth exceeded
            if depth > self.args.depth:
                continue
            
            # Check robots.txt
            if not self.can_fetch(url):
                self.log(f"Disallowed by robots.txt: {url}", "WARNING")
                continue
            
            # Mark as visited
            self.visited_urls.add(url)
            
            # Random delay between requests
            if self.pages_crawled > 0:  # Don't delay before first request
                delay = random.uniform(self.args.delay_min, self.args.delay_max)
                self.log(f"Waiting {delay:.2f} seconds before next request")
                time.sleep(delay)
            
            # Fetch the page
            content, status_code, content_type, content_length = self.fetch_page(url)
            
            if content is None:
                continue
            
            self.pages_crawled += 1
            if self.pbar:
                self.pbar.update(1)
            
            # Determine if this is a file to download or HTML to parse
            is_html = 'text/html' in content_type
            is_file = any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx'])
            
            if is_file or not is_html:
                # Download file
                saved_path = self.save_raw(content, url, is_file=True)
                self.log_metadata(url, status_code, content_type, saved_path, 
                                depth, parent_url, content_length)
            else:
                # Save HTML and parse links
                saved_path = self.save_raw(content, url, is_file=False)
                self.log_metadata(url, status_code, content_type, saved_path, 
                                depth, parent_url, content_length)
                
                # Parse links if we haven't reached max depth
                if depth < self.args.depth:
                    links = self.parse_links(content, url)
                    
                    # Add links to queue if they should be followed
                    for link in links:
                        if link not in self.visited_urls and self.should_follow(link, seed_url):
                            # Check if it's a file link
                            if any(ext in link.lower() for ext in ['.pdf', '.doc', '.docx']):
                                # Add file links at same depth (don't recurse from files)
                                queue.append((link, depth, url))
                            else:
                                # Add HTML links at next depth
                                queue.append((link, depth + 1, url))
        
        self.log(f"Completed crawl from seed: {seed_url}")
    
    def run(self):
        """Main entry point for the crawler."""
        seeds = self.read_seeds()
        
        if not seeds:
            self.log("No seeds to crawl", "ERROR")
            return
        
        self.log(f"Starting crawler with {len(seeds)} seed(s)")
        self.log(f"Max depth: {self.args.depth}, Max pages: {self.args.max_pages}")
        self.log(f"Delay range: {self.args.delay_min}-{self.args.delay_max} seconds")
        
        for seed in seeds:
            if self.args.max_pages > 0 and self.pages_crawled >= self.args.max_pages:
                self.log("Reached max pages limit", "INFO")
                break
            
            self.crawl_seed(seed)
        
        if self.pbar:
            self.pbar.close()
        
        self.log(f"Crawling complete. Total pages crawled: {self.pages_crawled}")


def main():
    """Parse command-line arguments and run the crawler."""
    parser = argparse.ArgumentParser(
        description='Web crawler that respects robots.txt and saves content with metadata',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--seeds',
        type=str,
        default='seeds.txt',
        help='Path to seeds file (one URL per line, # for comments)'
    )
    
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='Maximum crawl depth from each seed'
    )
    
    parser.add_argument(
        '--delay-min',
        type=float,
        default=1.0,
        help='Minimum delay between requests in seconds'
    )
    
    parser.add_argument(
        '--delay-max',
        type=float,
        default=3.0,
        help='Maximum delay between requests in seconds'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=0,
        help='Maximum number of pages to crawl (0 for unlimited)'
    )
    
    parser.add_argument(
        '--user-agent',
        type=str,
        default='Mozilla/5.0 (compatible; CustomCrawler/1.0)',
        help='User agent string to use for requests'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.delay_min < 0 or args.delay_max < 0:
        print("Error: Delay values must be non-negative", file=sys.stderr)
        sys.exit(1)
    
    if args.delay_min > args.delay_max:
        print("Error: --delay-min must be less than or equal to --delay-max", file=sys.stderr)
        sys.exit(1)
    
    if args.depth < 0:
        print("Error: Depth must be non-negative", file=sys.stderr)
        sys.exit(1)
    
    if args.max_pages < 0:
        print("Error: Max pages must be non-negative", file=sys.stderr)
        sys.exit(1)
    
    # Create and run crawler
    crawler = Crawler(args)
    crawler.run()


if __name__ == '__main__':
    main()
