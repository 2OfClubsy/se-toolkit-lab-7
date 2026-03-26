"""LMS API client module for backend communication.

This module provides an asynchronous HTTP client for interacting
with the LMS backend API using Bearer token authentication.
"""

import httpx


class LMSAPIClient:
    """Asynchronous client for LMS backend API operations.

    This client handles HTTP communication with the LMS backend,
    including health checks, lab enumeration, and score retrieval.

    Attributes:
        base_url: The root URL of the LMS API endpoint.
        api_key: Bearer token for API authentication.
    """

    def __init__(self, base_url: str, api_key: str):
        """Initialize the API client with authentication credentials.

        Args:
            base_url: The base URL of the LMS API (e.g., 'http://localhost:42002').
            api_key: The Bearer token for authenticating API requests.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )

    async def health_check(self) -> dict:
        """
        Verify backend availability by querying the /items endpoint.

        Returns:
            dict with keys:
                - ok (bool): True if backend responded successfully
                - status_code (int | None): HTTP response code if available
                - message (str): Human-readable status description
        """
        url = f"{self.base_url}/items/"
        try:
            response = await self._client.get(url)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "status_code": response.status_code,
                    "message": f"Backend is healthy (HTTP {response.status_code})",
                }
            else:
                return {
                    "ok": False,
                    "status_code": response.status_code,
                    "message": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "status_code": None,
                "message": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "status_code": None,
                "message": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "status_code": None,
                "message": "An unexpected error occurred while checking backend status.",
            }

    async def get_labs(self) -> dict:
        """
        Retrieve all laboratory assignments from the LMS API.

        Returns:
            dict with keys:
                - ok (bool): True if request completed successfully
                - labs (list[dict]): List of lab objects containing title and created_at
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/items/"
        try:
            response = await self._client.get(url)
            if response.status_code == 200:
                items = response.json()
                # Filter items by type == 'lab' and sort chronologically
                labs = [
                    item for item in items
                    if item.get("type") == "lab"
                ]
                labs.sort(key=lambda x: x.get("created_at", ""))
                return {
                    "ok": True,
                    "labs": labs,
                    "error": None,
                }
            else:
                return {
                    "ok": False,
                    "labs": [],
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "labs": [],
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "labs": [],
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "labs": [],
                "error": "An unexpected error occurred while fetching labs.",
            }

    async def get_items(self) -> dict:
        """
        Retrieve all items (labs and tasks) from the LMS API.

        Returns:
            dict with keys:
                - ok (bool): True if request completed successfully
                - items (list[dict]): List of all items
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/items/"
        try:
            response = await self._client.get(url)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "items": response.json(),
                    "error": None,
                }
            else:
                return {
                    "ok": False,
                    "items": [],
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "items": [],
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "items": [],
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "items": [],
                "error": "An unexpected error occurred while fetching items.",
            }

    async def get_learners(self) -> dict:
        """
        Retrieve all enrolled learners from the LMS API.

        Returns:
            dict with keys:
                - ok (bool): True if request completed successfully
                - learners (list[dict]): List of learner objects
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/learners/"
        try:
            response = await self._client.get(url)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "learners": response.json(),
                    "error": None,
                }
            else:
                return {
                    "ok": False,
                    "learners": [],
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "learners": [],
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "learners": [],
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "learners": [],
                "error": "An unexpected error occurred while fetching learners.",
            }

    async def get_pass_rates(self, lab: str) -> dict:
        """
        Retrieve per-task pass rates for a specified laboratory.

        Args:
            lab: The laboratory identifier (e.g., 'lab-01').

        Returns:
            dict with keys:
                - ok (bool): True if request completed successfully
                - pass_rates (list[dict]): List of task pass rates
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/analytics/pass-rates"
        params = {"lab": lab}
        try:
            response = await self._client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                pass_rates = data if isinstance(data, list) else data.get("scores", [data] if data else [])
                return {
                    "ok": True,
                    "pass_rates": pass_rates,
                    "error": None,
                }
            elif response.status_code == 404:
                return {
                    "ok": False,
                    "pass_rates": [],
                    "error": f"Lab '{lab}' not found.",
                }
            else:
                return {
                    "ok": False,
                    "pass_rates": [],
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "pass_rates": [],
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "pass_rates": [],
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "pass_rates": [],
                "error": "An unexpected error occurred while fetching pass rates.",
            }

    async def get_timeline(self, lab: str) -> dict:
        """
        Retrieve submission timeline for a specified laboratory.

        Args:
            lab: The laboratory identifier (e.g., 'lab-01').

        Returns:
            dict with keys:
                - ok (bool): True if request completed successfully
                - timeline (list[dict]): List of daily submission counts
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/analytics/timeline"
        params = {"lab": lab}
        try:
            response = await self._client.get(url, params=params)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "timeline": response.json(),
                    "error": None,
                }
            elif response.status_code == 404:
                return {
                    "ok": False,
                    "timeline": [],
                    "error": f"Lab '{lab}' not found.",
                }
            else:
                return {
                    "ok": False,
                    "timeline": [],
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "timeline": [],
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "timeline": [],
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "timeline": [],
                "error": "An unexpected error occurred while fetching timeline.",
            }

    async def get_groups(self, lab: str) -> dict:
        """
        Retrieve per-group scores for a specified laboratory.

        Args:
            lab: The laboratory identifier (e.g., 'lab-01').

        Returns:
            dict with keys:
                - ok (bool): True if request completed successfully
                - groups (list[dict]): List of group scores and student counts
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/analytics/groups"
        params = {"lab": lab}
        try:
            response = await self._client.get(url, params=params)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "groups": response.json(),
                    "error": None,
                }
            elif response.status_code == 404:
                return {
                    "ok": False,
                    "groups": [],
                    "error": f"Lab '{lab}' not found.",
                }
            else:
                return {
                    "ok": False,
                    "groups": [],
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "groups": [],
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "groups": [],
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "groups": [],
                "error": "An unexpected error occurred while fetching groups.",
            }

    async def get_top_learners(self, lab: str, limit: int = 10) -> dict:
        """
        Retrieve top-performing learners for a specified laboratory.

        Args:
            lab: The laboratory identifier (e.g., 'lab-01').
            limit: Maximum number of learners to return (default: 10).

        Returns:
            dict with keys:
                - ok (bool): True if request completed successfully
                - top_learners (list[dict]): List of top learners with scores
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/analytics/top-learners"
        params = {"lab": lab, "limit": limit}
        try:
            response = await self._client.get(url, params=params)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "top_learners": response.json(),
                    "error": None,
                }
            elif response.status_code == 404:
                return {
                    "ok": False,
                    "top_learners": [],
                    "error": f"Lab '{lab}' not found.",
                }
            else:
                return {
                    "ok": False,
                    "top_learners": [],
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "top_learners": [],
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "top_learners": [],
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "top_learners": [],
                "error": "An unexpected error occurred while fetching top learners.",
            }

    async def get_completion_rate(self, lab: str) -> dict:
        """
        Retrieve completion rate for a specified laboratory.

        Args:
            lab: The laboratory identifier (e.g., 'lab-01').

        Returns:
            dict with keys:
                - ok (bool): True if request completed successfully
                - completion_rate (float): Completion rate percentage
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/analytics/completion-rate"
        params = {"lab": lab}
        try:
            response = await self._client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if isinstance(data, dict):
                    rate = data.get("rate", data.get("completion_rate", 0))
                else:
                    rate = data if isinstance(data, (int, float)) else 0
                return {
                    "ok": True,
                    "completion_rate": rate,
                    "error": None,
                }
            elif response.status_code == 404:
                return {
                    "ok": False,
                    "completion_rate": 0,
                    "error": f"Lab '{lab}' not found.",
                }
            else:
                return {
                    "ok": False,
                    "completion_rate": 0,
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "completion_rate": 0,
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "completion_rate": 0,
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "completion_rate": 0,
                "error": "An unexpected error occurred while fetching completion rate.",
            }

    async def trigger_sync(self) -> dict:
        """
        Trigger a data synchronization from the autochecker.

        Returns:
            dict with keys:
                - ok (bool): True if sync was triggered
                - status (str | None): Sync status message
                - error (str | None): Error description if request failed
        """
        url = f"{self.base_url}/pipeline/sync"
        try:
            response = await self._client.post(url)
            if response.status_code in (200, 201, 202):
                data = response.json() if response.content else {}
                return {
                    "ok": True,
                    "status": data.get("status", "Sync triggered"),
                    "error": None,
                }
            else:
                return {
                    "ok": False,
                    "status": None,
                    "error": self._format_error_response(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "status": None,
                "error": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "status": None,
                "error": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "status": None,
                "error": "An unexpected error occurred while triggering sync.",
            }

    def _format_error_response(self, status_code: int) -> str:
        """Generate a descriptive error message for an HTTP status code.

        Args:
            status_code: The HTTP response status code.

        Returns:
            A user-friendly error description.
        """
        error_messages = {
            400: "Bad Gateway (400): The backend received an invalid request.",
            401: "Unauthorized (401): API key is missing or invalid.",
            403: "Forbidden (403): Access denied. Check API key permissions.",
            404: "Not Found (404): The requested resource does not exist.",
            500: "Internal Server Error (500): The backend encountered an error.",
            502: "Bad Gateway (502): The backend service may be down or unreachable.",
            503: "Service Unavailable (503): The backend is temporarily unavailable.",
            504: "Gateway Timeout (504): The backend took too long to respond.",
        }
        return error_messages.get(
            status_code,
            f"Backend error: HTTP {status_code}. Please try again later.",
        )

    async def close(self):
        """Terminate the HTTP client session and release resources."""
        await self._client.aclose()
