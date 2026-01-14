"""
Export package for static site generation.

This package provides functionality to export Wagtail sites to standalone
HTML archives that can be browsed offline.
"""

class ExportError(Exception):
    """Base exception for export-related errors"""
    pass
