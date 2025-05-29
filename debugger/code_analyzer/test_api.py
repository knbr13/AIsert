import requests
from typing import Dict, Any
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class TestAPI:
    def __init__(self):
        # Get timeout from environment variable or use default
        self.timeout = int(os.getenv('API_TIMEOUT', 10))  # Increased default timeout to 10 seconds
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[500, 502, 503, 504],  # retry on these status codes
            allowed_methods=["GET", "POST", "PUT", "DELETE"]  # allow retries on all methods
        )
        
        # Create session with retry strategy
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CodeAnalyzer/1.0"  # Add user agent
        })

    def test_endpoint(self, url: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """
        Test an API endpoint with retry logic.
        
        Args:
            url (str): API endpoint URL
            method (str): HTTP method (GET, POST, etc.)
            data (Dict): Request data for POST/PUT methods
            
        Returns:
            Dict[str, Any]: Test results
        """
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=self.timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=self.timeout)
            else:
                return {"error": f"Unsupported method: {method}"}

            # Check if response is successful
            response.raise_for_status()

            return {
                "status": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.headers.get("content-type") == "application/json" else response.text,
                "elapsed_time": response.elapsed.total_seconds(),
                "endpoint": url
            }

        except requests.exceptions.Timeout:
            return {
                "error": f"Request timed out after {self.timeout} seconds",
                "status": None,
                "suggestion": "Try increasing the API_TIMEOUT environment variable or check the API endpoint's response time.",
                "endpoint": url
            }
        except requests.exceptions.ConnectionError:
            return {
                "error": "Connection error. Please check your internet connection and the API endpoint.",
                "status": None,
                "suggestion": "Verify the API endpoint URL and ensure you have a stable internet connection.",
                "endpoint": url
            }
        except requests.exceptions.HTTPError as e:
            return {
                "error": f"HTTP Error: {str(e)}",
                "status": e.response.status_code if hasattr(e, 'response') else None,
                "suggestion": "The API endpoint returned an error. Try again later or use a different endpoint.",
                "endpoint": url
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": getattr(e.response, "status_code", None) if hasattr(e, "response") else None,
                "suggestion": "Check the API endpoint configuration and try again.",
                "endpoint": url
            }

    def validate_response(self, response: Dict[str, Any], expected_status: int = 200) -> Dict[str, Any]:
        """
        Validate API response.
        
        Args:
            response (Dict[str, Any]): API response
            expected_status (int): Expected HTTP status code
            
        Returns:
            Dict[str, Any]: Validation results
        """
        validation = {
            "passed": False,
            "checks": []
        }

        # Check if there was an error
        if "error" in response:
            validation["checks"].append({
                "name": "Error Check",
                "expected": "No errors",
                "actual": response["error"],
                "passed": False,
                "suggestion": response.get("suggestion", "No specific suggestion available.")
            })
            return validation

        # Check status code
        status_check = {
            "name": "Status Code",
            "expected": expected_status,
            "actual": response.get("status"),
            "passed": response.get("status") == expected_status
        }
        validation["checks"].append(status_check)

        # Check response time
        time_check = {
            "name": "Response Time",
            "expected": f"< {self.timeout}s",
            "actual": f"{response.get('elapsed_time', 0):.2f}s",
            "passed": response.get("elapsed_time", 0) < self.timeout
        }
        validation["checks"].append(time_check)

        # Check content type
        content_type = response.get("headers", {}).get("content-type", "")
        content_check = {
            "name": "Content Type",
            "expected": "application/json",
            "actual": content_type,
            "passed": "application/json" in content_type
        }
        validation["checks"].append(content_check)

        # Overall validation result
        validation["passed"] = all(check["passed"] for check in validation["checks"])

        return validation 