#!/usr/bin/env python3
"""
Basic test to validate the simplified bookstore module
"""

import os
import sys

def test_module_structure():
    """Test if the basic module structure is correct"""
    print("=== Testing Basic Module Structure ===")
    
    # Check if required directories exist
    required_dirs = [
        'bookstore',
        'bookstore/models',
        'bookstore/views', 
        'bookstore/controllers',
        'bookstore/data',
        'bookstore/security'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ Directory exists: {dir_path}")
        else:
            print(f"✗ Missing directory: {dir_path}")
            return False
    
    # Check if required files exist
    required_files = [
        'bookstore/__manifest__.py',
        'bookstore/__init__.py',
        'bookstore/models/__init__.py',
        'bookstore/models/book.py',
        'bookstore/controllers/__init__.py',
        'bookstore/controllers/main.py',
        'bookstore/views/book_view.xml',
        'bookstore/views/website_templates.xml',
        'bookstore/security/ir.model.access.csv'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ File exists: {file_path}")
        else:
            print(f"✗ Missing file: {file_path}")
            return False
    
    print("\n=== Testing File Contents ===")
    
    # Test manifest file
    try:
        with open('bookstore/__manifest__.py', 'r') as f:
            manifest_content = f.read()
            if "'bookstore'" in manifest_content and "'base'" in manifest_content:
                print("✓ Manifest file looks good")
            else:
                print("✗ Manifest file has issues")
                return False
    except Exception as e:
        print(f"✗ Error reading manifest: {e}")
        return False
    
    # Test model file
    try:
        with open('bookstore/models/book.py', 'r') as f:
            model_content = f.read()
            if "class Book" in model_content and "_name = 'bookstore.book'" in model_content:
                print("✓ Book model looks good")
            else:
                print("✗ Book model has issues")
                return False
    except Exception as e:
        print(f"✗ Error reading book model: {e}")
        return False
    
    print("\n=== All Tests Passed! ===")
    print("The basic module structure is correct.")
    return True

if __name__ == "__main__":
    success = test_module_structure()
    sys.exit(0 if success else 1)
