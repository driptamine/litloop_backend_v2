import os
import re


# Handles channel_binding and Neon SNI requirements before DB config uses it
_db_url = os.environ.get('DATABASE_URL')
if _db_url:
    if 'channel_binding=' in _db_url:
        _db_url = re.sub(r'[?&]channel_binding=[^&]+', '', _db_url)
    if 'neon.tech' in _db_url and 'options=endpoint' not in _db_url:
        match = re.search(r'@([^.]+)', _db_url)
        if match:
            endpoint_id = match.group(1)
            separator = '&' if '?' in _db_url else '?'
            _db_url += f"{separator}options=endpoint%3D{endpoint_id}"
    os.environ['DATABASE_URL'] = _db_url
