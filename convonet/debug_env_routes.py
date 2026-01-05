"""
Debug routes to check environment variables
Useful for diagnosing why environment variables aren't being read
"""

from flask import Blueprint, jsonify
import os

debug_env_bp = Blueprint('debug_env', __name__, url_prefix='/debug/env')

@debug_env_bp.route('/google', methods=['GET'])
def debug_google_env():
    """Check Google Calendar related environment variables"""
    env_vars = {
        'GOOGLE_OAUTH2_TOKEN_B64': {
            'set': bool(os.getenv('GOOGLE_OAUTH2_TOKEN_B64')),
            'length': len(os.getenv('GOOGLE_OAUTH2_TOKEN_B64', '')),
            'preview': os.getenv('GOOGLE_OAUTH2_TOKEN_B64', '')[:50] + '...' if os.getenv('GOOGLE_OAUTH2_TOKEN_B64') else None
        },
        'GOOGLE_CREDENTIALS_B64': {
            'set': bool(os.getenv('GOOGLE_CREDENTIALS_B64')),
            'length': len(os.getenv('GOOGLE_CREDENTIALS_B64', ''))
        },
        'GOOGLE_TOKEN_B64': {
            'set': bool(os.getenv('GOOGLE_TOKEN_B64')),
            'length': len(os.getenv('GOOGLE_TOKEN_B64', ''))
        },
        'GOOGLE_CLIENT_ID': {
            'set': bool(os.getenv('GOOGLE_CLIENT_ID')),
            'value': os.getenv('GOOGLE_CLIENT_ID', '')[:50] + '...' if os.getenv('GOOGLE_CLIENT_ID') and len(os.getenv('GOOGLE_CLIENT_ID', '')) > 50 else os.getenv('GOOGLE_CLIENT_ID', '')
        },
        'GOOGLE_CLIENT_SECRET': {
            'set': bool(os.getenv('GOOGLE_CLIENT_SECRET')),
            'length': len(os.getenv('GOOGLE_CLIENT_SECRET', ''))
        }
    }
    
    # Also check all environment variables that contain "GOOGLE"
    all_google_vars = {k: 'SET' if v else 'NOT SET' for k, v in os.environ.items() if 'GOOGLE' in k.upper()}
    
    return jsonify({
        'status': 'success',
        'variables': env_vars,
        'all_google_variables_in_env': all_google_vars,
        'total_env_vars': len(os.environ),
        'python_version': os.sys.version if hasattr(os, 'sys') else 'unknown'
    })

@debug_env_bp.route('/all', methods=['GET'])
def debug_all_env():
    """List all environment variables (be careful - don't expose sensitive data in production)"""
    # Only show variable names, not values for security
    return jsonify({
        'status': 'success',
        'env_var_names': sorted(list(os.environ.keys())),
        'total_count': len(os.environ)
    })

@debug_env_bp.route('/check', methods=['GET'])
def debug_check_specific():
    """Check if specific environment variable is set"""
    from flask import request
    var_name = request.args.get('var', '')
    
    if not var_name:
        return jsonify({
            'error': 'Please provide ?var=VARIABLE_NAME parameter'
        }), 400
    
    value = os.getenv(var_name)
    return jsonify({
        'variable': var_name,
        'set': bool(value),
        'length': len(value) if value else 0,
        'preview': value[:100] + '...' if value and len(value) > 100 else value
    })

