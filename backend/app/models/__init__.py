"""SQLAlchemy models for the AI Marketing Assistant.

DEPRECATED: This module is kept for backward compatibility only.
Use app.models.async_models for all new development.
"""

# Import async models for backward compatibility
from app.models.async_models import *

# Keep the legacy imports for any code that still depends on them
# These will be removed in a future version
try:
    from app.models.user import User as LegacyUser
    from app.models.content import Organization as LegacyOrganization
    # Add any other legacy imports as needed
except ImportError:
    # Legacy models may not be available if database.py is removed
    pass