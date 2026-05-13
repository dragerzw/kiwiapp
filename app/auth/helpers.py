def get_normalized_groups(claims: dict) -> list[str]:
    """Parse and normalize groups from Cognito claims."""
    groups = claims.get('cognito:groups') or claims.get('groups') or []
    if isinstance(groups, str):
        return [groups]
    if isinstance(groups, (list, tuple, set)):
        return [group for group in groups if isinstance(group, str)]
    return []

def is_admin(claims: dict) -> bool:
    """Check if the user has an admin group in their claims."""
    admin_group_names = {'Admins', 'Admin', 'Administrators', 'Administrator'}
    groups = get_normalized_groups(claims)
    return any(group in admin_group_names for group in groups)
