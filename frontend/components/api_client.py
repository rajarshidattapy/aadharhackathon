"""
API Client for communicating with the FastAPI backend.
Handles all HTTP requests, caching, and error handling.
"""

import os
import requests
import streamlit as st
from typing import Optional, Dict, Any


def get_backend_url() -> str:
    """Get backend URL from session state or environment variable."""
    if "backend_url" in st.session_state and st.session_state.backend_url:
        return st.session_state.backend_url
    return os.environ.get("BACKEND_URL", "http://127.0.0.1:8001")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_alerts(endpoint: str, month: Optional[str] = None, _backend_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch alerts from the FastAPI backend.

    Args:
        endpoint: API endpoint path (e.g., "/migration", "/infrastructure")
        month: Optional month filter in YYYY-MM format. If "Latest" or None, no filter applied.
        _backend_url: Backend URL (prefixed with _ to exclude from cache key in newer Streamlit)

    Returns:
        Dict containing the API response with 'month' and 'alerts' keys

    Raises:
        Exception: If API request fails
    """
    backend_url = _backend_url or get_backend_url()
    url = f"{backend_url.rstrip('/')}{endpoint}"

    params = {}
    if month and month.lower() != "latest":
        params["month"] = month

    try:
        # Use longer timeout for first request (data loading may take time)
        # First request might need to download 158MB CSV file
        timeout = 120 if not hasattr(fetch_alerts, '_first_request_done') else 30
        response = requests.get(url, params=params, timeout=timeout)
        fetch_alerts._first_request_done = True
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception(
            f"Request timeout: The server took too long to respond. "
            f"This may happen on the first request while downloading the dataset (158MB). "
            f"Please wait a few minutes and try again."
        )
    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Connection error: Could not connect to {url}. "
            f"Please verify the backend URL is correct and the server is running."
        )
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else None
        if status_code == 404:
            raise Exception(f"Not found: Endpoint {endpoint} does not exist")
        elif status_code == 500:
            raise Exception(
                f"Server error: The backend encountered an error. "
                f"This may occur during initial data loading. Please try again in a few moments."
            )
        elif status_code == 502:
            raise Exception(
                f"Bad Gateway (502): The backend server is not responding. "
                f"This may happen if: (1) The backend is starting up and loading data, "
                f"(2) The backend crashed, or (3) There's a network issue. "
                f"Please check the backend status and try again in a few minutes."
            )
        else:
            error_text = e.response.text[:200] if e.response else str(e)
            raise Exception(f"HTTP error {status_code}: {error_text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")


def test_connection(backend_url: str) -> tuple[bool, str]:
    """
    Test connection to the backend server.

    Args:
        backend_url: The backend URL to test

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        response = requests.get(f"{backend_url.rstrip('/')}/health", timeout=10)
        if response.status_code == 200:
            return True, "✅ Connection successful!"
        else:
            return False, f"⚠️ Server responded with status {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "❌ Connection timeout - Backend may be loading data. Please wait and try again."
    except requests.exceptions.ConnectionError:
        return False, f"❌ Could not connect to {backend_url}. Please verify the URL is correct."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def clear_cache():
    """Clear all cached API data."""
    fetch_alerts.clear()


# Endpoint mappings
ENDPOINTS = {
    "migration": "/alerts/migration",
    "infrastructure": "/alerts/infrastructure",
    "biometric": "/alerts/biometric-integrity",
    "lost_generation": "/alerts/lost-generation",
    "migration_ml": "/alerts/migration-ml",
}


def fetch_migration_alerts(month: Optional[str] = None) -> Dict[str, Any]:
    """Fetch migration URRDF alerts."""
    return fetch_alerts(ENDPOINTS["migration"], month, get_backend_url())


def fetch_infrastructure_alerts(month: Optional[str] = None) -> Dict[str, Any]:
    """Fetch infrastructure AFLB alerts."""
    return fetch_alerts(ENDPOINTS["infrastructure"], month, get_backend_url())


def fetch_biometric_alerts(month: Optional[str] = None) -> Dict[str, Any]:
    """Fetch biometric integrity BIS alerts."""
    return fetch_alerts(ENDPOINTS["biometric"], month, get_backend_url())


def fetch_lost_generation_alerts(month: Optional[str] = None) -> Dict[str, Any]:
    """Fetch lost generation FAFI alerts."""
    return fetch_alerts(ENDPOINTS["lost_generation"], month, get_backend_url())


def fetch_ml_alerts(month: Optional[str] = None) -> Dict[str, Any]:
    """Fetch ML-based migration forecast alerts."""
    return fetch_alerts(ENDPOINTS["migration_ml"], month, get_backend_url())

