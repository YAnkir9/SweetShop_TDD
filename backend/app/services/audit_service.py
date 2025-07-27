"""Audit Service - For tracking admin actions"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def log_admin_action(admin_id: int, action: str, details: Dict[str, Any] = None):
    """
    Log admin actions for audit trail.
    
    Args:
        admin_id: ID of the admin user performing the action
        action: The action being performed
        details: Additional details about the action
    """
    timestamp = datetime.utcnow().isoformat()
    
    # In a real implementation, this would save to a database
    # For now, we'll just log it
    log_message = f"AUDIT: Admin {admin_id} performed '{action}' at {timestamp}"
    if details:
        log_message += f" - Details: {details}"
    
    logger.info(log_message)
    
    # In production, this would save to an audit_logs table:
    # audit_entry = AuditLog(
    #     admin_id=admin_id,
    #     action=action,
    #     details=json.dumps(details) if details else None,
    #     timestamp=datetime.utcnow()
    # )
    # await db.add(audit_entry)
    # await db.commit()
