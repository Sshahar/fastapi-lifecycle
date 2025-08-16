"""HTTP header utilities for API lifecycle management."""

from datetime import datetime
from typing import Union

from dateutil import parser


class VersioningHeaders:
    """Utility class for managing versioning-related HTTP headers."""

    @staticmethod
    def format_http_date(dt: Union[datetime, str]) -> str:
        """
        Format datetime to RFC 7231 compliant HTTP date format.

        Args:
            dt: Datetime object or ISO 8601 string to format

        Returns:
            HTTP date string in format: "Wed, 21 Oct 2015 07:28:00 GMT"

        Examples:
            >>> VersioningHeaders.format_http_date("2024-01-15T00:00:00Z")
            "Mon, 15 Jan 2024 00:00:00 GMT"
        """
        if isinstance(dt, str):
            dt = parser.isoparse(dt.replace("Z", "+00:00"))
        return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

    @staticmethod
    def create_link_header(url: str, rel: str = "deprecation") -> str:
        """
        Create RFC 8288 compliant Link header value.

        Args:
            url: Target URL for the link
            rel: Link relation type (default: "deprecation")

        Returns:
            Formatted Link header value

        Examples:
            >>> VersioningHeaders.create_link_header("https://api.example.com/docs")
            '<https://api.example.com/docs>; rel="deprecation"'
        """
        return f'<{url}>; rel="{rel}"'
