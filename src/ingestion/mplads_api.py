import requests


BASE_URL = "https://mplads.mospi.gov.in"

SESSION_URL = f"{BASE_URL}/digigov/dashboard.html"

REPORT_URL = (
    f"{BASE_URL}/rest/PreLoginDashboardData/"
    "getTilesReportData"
)


class MPLADSClient:
    """Client for the official MPLADS public API."""

    def __init__(self):
        self.session = requests.Session()

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
        """Fetch one MPLADS report for the 18th Lok Sabha."""

        payload = {
            "combo": "0,0,0,2,7",
            "key": key,
        }

        response = self.session.post(
            REPORT_URL,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        return response.json()