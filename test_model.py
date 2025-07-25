#!/usr/bin/env python3
"""
Simple validation script to test if our model definitions are syntactically correct
"""

import sys
import os

# Add the bookstore module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bookstore'))

try:
    # Try to import the models
    print("Testing model imports...")
    
    # Test if we can import the basic structure
    import models
    print("✓ Models package imported successfully")
    
    # Test specific model imports
    from models import book
    print("✓ Book model imported successfully")
    
    print("\nAll imports successful! The model structure looks good.")
    
except ImportError as e:
    print(f"✗ Import Error: {e}")
    print("This indicates a problem with the model structure.")
except SyntaxError as e:
    print(f"✗ Syntax Error: {e}")
    print("This indicates a syntax problem in the Python files.")
except Exception as e:
    print(f"✗ Other Error: {e}")
    print("This indicates another issue with the model files.")
