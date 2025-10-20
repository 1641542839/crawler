#!/usr/bin/env python3
"""
Simple tests for the crawler module.
Tests key functionality without requiring external dependencies.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after adding to path
import crawler


def test_should_follow():
    """Test the should_follow logic."""
    print("Testing should_follow...")
    
    # Create a mock args object
    class MockArgs:
        seeds = "seeds.txt"
        depth = 3
        delay_min = 1.0
        delay_max = 3.0
        max_pages = 0
        user_agent = "Test"
        verbose = False
    
    c = crawler.Crawler(MockArgs())
    
    # Test same hostname and path prefix
    assert c.should_follow(
        "https://example.com/docs/page1",
        "https://example.com/docs/"
    ), "Should follow same hostname and path prefix"
    
    # Test different hostname
    assert not c.should_follow(
        "https://other.com/docs/",
        "https://example.com/docs/"
    ), "Should not follow different hostname"
    
    # Test wrong path prefix
    assert not c.should_follow(
        "https://example.com/blog/",
        "https://example.com/docs/"
    ), "Should not follow wrong path prefix"
    
    # Test root path allows all
    assert c.should_follow(
        "https://example.com/anything",
        "https://example.com/"
    ), "Root path should allow any path"
    
    print("✓ should_follow tests passed")


def test_parse_links():
    """Test link parsing."""
    print("Testing parse_links...")
    
    class MockArgs:
        seeds = "seeds.txt"
        depth = 3
        delay_min = 1.0
        delay_max = 3.0
        max_pages = 0
        user_agent = "Test"
        verbose = False
    
    c = crawler.Crawler(MockArgs())
    
    html = b'''
    <html>
    <body>
        <a href="/page1">Page 1</a>
        <a href="/page2">Page 2</a>
        <a href="https://example.com/page3">Page 3</a>
        <a href="#anchor">Anchor</a>
    </body>
    </html>
    '''
    
    links = c.parse_links(html, "https://example.com/")
    
    assert "https://example.com/page1" in links, "Should find relative link 1"
    assert "https://example.com/page2" in links, "Should find relative link 2"
    assert "https://example.com/page3" in links, "Should find absolute link"
    # Anchors are stripped, so just the base URL should be in links
    
    print("✓ parse_links tests passed")


def test_read_seeds():
    """Test reading seeds from file."""
    print("Testing read_seeds...")
    
    # Create a temporary seeds file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("# Comment line\n")
        f.write("https://example.com/\n")
        f.write("\n")  # Empty line
        f.write("https://test.com/\n")
        f.write("# Another comment\n")
        temp_file = f.name
    
    try:
        class MockArgs:
            seeds = temp_file
            depth = 3
            delay_min = 1.0
            delay_max = 3.0
            max_pages = 0
            user_agent = "Test"
            verbose = False
        
        c = crawler.Crawler(MockArgs())
        seeds = c.read_seeds()
        
        assert len(seeds) == 2, f"Should find 2 seeds, found {len(seeds)}"
        assert "https://example.com/" in seeds, "Should find first seed"
        assert "https://test.com/" in seeds, "Should find second seed"
        
        print("✓ read_seeds tests passed")
    finally:
        os.unlink(temp_file)


def test_save_raw():
    """Test saving raw content."""
    print("Testing save_raw...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(temp_dir)
        
        class MockArgs:
            seeds = "seeds.txt"
            depth = 3
            delay_min = 1.0
            delay_max = 3.0
            max_pages = 0
            user_agent = "Test"
            verbose = False
        
        c = crawler.Crawler(MockArgs())
        
        # Test HTML save
        content = b"<html><body>Test</body></html>"
        url = "https://example.com/page1"
        path = c.save_raw(content, url, is_file=False)
        
        assert os.path.exists(path), f"HTML file should exist at {path}"
        with open(path, 'rb') as f:
            assert f.read() == content, "Content should match"
        
        # Test file save
        pdf_content = b"%PDF-1.4\nTest PDF"
        pdf_url = "https://example.com/doc.pdf"
        pdf_path = c.save_raw(pdf_content, pdf_url, is_file=True)
        
        assert os.path.exists(pdf_path), f"PDF file should exist at {pdf_path}"
        assert pdf_path.endswith('.pdf'), "Should have .pdf extension"
        with open(pdf_path, 'rb') as f:
            assert f.read() == pdf_content, "PDF content should match"
        
        print("✓ save_raw tests passed")
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    print("Running crawler tests...\n")
    
    try:
        test_should_follow()
        test_parse_links()
        test_read_seeds()
        test_save_raw()
        
        print("\n✓ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
