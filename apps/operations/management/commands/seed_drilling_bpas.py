"""
Alias command for populate_drilling_bpa.
Enables running `python manage.py seed_drilling_bpas` as well as `populate_drilling_bpa`.
"""

from apps.operations.management.commands.populate_drilling_bpa import Command

__all__ = ["Command"]
