import requests
import time
import json


BASE_URL = "https://mplads.mospi.gov.in"

SESSION_URL = f"{BASE_URL}/digigov/dashboard.html"

REPORT_URL = (
    f"{BASE_URL}/rest/PreLoginDashboardData/"
    "getTilesReportData"
)


class MPLADSClient:
    """Client for the official MPLADS public API."""

    def __init__(self, combo="21,245,0,2,7"):
        """Initialize client with optional filter combo.

        Args:
            combo (str): Filter string for API request. Defaults to
                         "21,245,0,2,7" (Maharashtra, Raver, 18th Lok Sabha)
                         which returns a small, reliable sample.
        """
        self.session = requests.Session()
        self.combo = combo

        self.session.headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": BASE_URL,
            "Referer": SESSION_URL,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            "X-Requested-With": "XMLHttpRequest",
        })

    def initialize_session(self):
        """Initialize a session with the MPLADS website."""

        response = self.session.get(
            SESSION_URL,
            timeout=30,
        )

        response.raise_for_status()

        print("MPLADS session initialized.")
        print("Cookies:", list(self.session.cookies.keys()))

    def fetch_report(self, key):
        """Fetch one MPLADS report for the configured filter.

        Returns:
            list: List of record dictionaries, or empty list if no data.
        """

        payload = {
            "combo": self.combo,
            "key": key,
        }

        response = self.session.post(
            REPORT_URL,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        # Parse the response
        result = response.json()
        
        # Extract the actual data from the response
        # The API returns a dict like {"Total Works Recommended": "[{...}]"}
        if isinstance(result, dict) and len(result) == 1:
            # Get the first (and only) key-value pair
            key_name, value = next(iter(result.items()))
            # The value should be a JSON string containing the array
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse JSON string for key {key_name}")
                    return []
            else:
                return value if isinstance(value, list) else []
        elif isinstance(result, list):
            # Already a list, return as-is
            return result
        else:
            # Unexpected format, return empty list
            print(f"Warning: Unexpected response format for key {key}")
            print(f"  Result type: {type(result)}")
            if isinstance(result, dict):
                print(f"  Keys: {list(result.keys())}")
            return []


# Test with actual API
if __name__ == "__main__":
    client = MPLADSClient()
    client.initialize_session()
    
    print("\n=== Testing All Endpoints ===")
    for endpoint in ["Works Recommended", "Works Completed", "Expenditure Incurred"]:
        print(f"\n{endpoint}:")
        try:
            data = client.fetch_report(endpoint)
            print(f"  Records: {len(data)}")
            if data:
                print(f"  First record keys: {list(data[0].keys())}")
        except Exception as e:
            print(f"  Error: {e}")