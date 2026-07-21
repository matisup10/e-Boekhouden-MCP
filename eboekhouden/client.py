"""Main client for the e-Boekhouden SDK."""

import logging
import re
import threading
import time

import httpx
from typing_extensions import Self

from eboekhouden.config import EBoekhoudenConfig
from eboekhouden.exceptions import AuthenticationError
from eboekhouden.services.administration import AdministrationService
from eboekhouden.services.cost_center import CostCenterService
from eboekhouden.services.email_template import EmailTemplateService
from eboekhouden.services.invoice import InvoiceService
from eboekhouden.services.invoice_template import InvoiceTemplateService
from eboekhouden.services.ledger import LedgerService
from eboekhouden.services.member import MemberService
from eboekhouden.services.mutation import MutationService
from eboekhouden.services.product import ProductService
from eboekhouden.services.relation import RelationService
from eboekhouden.services.unit import UnitService

logger = logging.getLogger(__name__)


def _normalize_session_source(source: str | None) -> str:
    r"""e-Boekhouden requires source to match ^[\w_ ]{1,10}$."""
    cleaned = re.sub(r"[^\w_ ]+", "", source or "").strip()
    return (cleaned or "PySDK")[:10]


class EBoekhoudenClient:
    """Client for the e-Boekhouden API with automatic session management.

    Usage:
        # Using context manager (recommended)
        with EBoekhoudenClient() as client:
            relations = client.relations.list()

        # Manual management
        client = EBoekhoudenClient()
        try:
            relations = client.relations.list()
        finally:
            client.close()
    """

    def __init__(
        self,
        *,
        secret_token: str | None = None,
        api_url: str | None = None,
        source: str | None = None,
        session_refresh_buffer: int | None = None,
    ):
        """Initialize the client.

        Args:
            secret_token: API secret token (or set EBOEKHOUDEN_SECRET_TOKEN env var)
            api_url: API base URL (default: https://api.e-boekhouden.nl/)
            source: Source identifier (default: PythonSDK)
            session_refresh_buffer: Seconds before expiry to refresh session (default: 60)
        """
        self._config = EBoekhoudenConfig(
            **({"secret_token": secret_token} if secret_token else {}),
            **({"api_url": api_url} if api_url else {}),
            **({"source": _normalize_session_source(source)} if source else {}),
            **(
                {"session_refresh_buffer": session_refresh_buffer}
                if session_refresh_buffer
                else {}
            ),
        )
        self._config.source = _normalize_session_source(self._config.source)

        self._session_lock = threading.RLock()
        self._http: httpx.Client | None = self._build_http_client()

        self._session_token: str | None = None
        self._session_expires_at: float = 0

        # Lazy-loaded services
        self._administrations: AdministrationService | None = None
        self._cost_centers: CostCenterService | None = None
        self._email_templates: EmailTemplateService | None = None
        self._invoice_templates: InvoiceTemplateService | None = None
        self._invoices: InvoiceService | None = None
        self._ledgers: LedgerService | None = None
        self._members: MemberService | None = None
        self._mutations: MutationService | None = None
        self._products: ProductService | None = None
        self._relations: RelationService | None = None
        self._units: UnitService | None = None

    def _build_http_client(self) -> httpx.Client:
        """Create a fresh HTTP client for the configured API."""
        return httpx.Client(
            base_url=self._config.api_url.rstrip("/"),
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    def _ensure_http_client(self) -> httpx.Client:
        """Lazily recreate the underlying HTTP client after close()."""
        if self._http is None:
            self._http = self._build_http_client()
        return self._http

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and close session."""
        self.close()

    def close(self) -> None:
        """Close the session and HTTP client."""
        with self._session_lock:
            self._discard_session(delete_remote=True)
            if self._http is not None:
                self._http.close()
                self._http = None

    def _discard_session(self, *, delete_remote: bool) -> None:
        """Forget the current session, optionally revoking it first."""
        token = self._session_token
        self._session_token = None
        self._session_expires_at = 0
        if not token or not delete_remote:
            return
        try:
            self._ensure_http_client().delete(
                "/v1/session",
                headers={"Authorization": token},
            )
        except Exception:
            logger.debug("Could not revoke e-Boekhouden session", exc_info=True)

    def _create_session(self) -> None:
        """Create a new API session."""
        with self._session_lock:
            response = self._ensure_http_client().post(
                "/v1/session",
                json={
                    "accessToken": self._config.secret_token.get_secret_value(),
                    "source": self._config.source,
                },
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid access token")
            if response.status_code >= 400:
                raise AuthenticationError(
                    f"Failed to create session (HTTP {response.status_code})"
                )

            try:
                data = response.json()
                token = data["token"]
                expires_in = float(data["expiresIn"])
            except (KeyError, TypeError, ValueError) as exc:
                raise AuthenticationError("Invalid session response") from exc
            if not isinstance(token, str) or not token or expires_in <= 0:
                raise AuthenticationError("Invalid session response")

            self._session_token = token
            self._session_expires_at = time.time() + expires_in

    def _ensure_session(self) -> None:
        """Ensure we have a valid session, refreshing if needed."""
        with self._session_lock:
            buffer = self._config.session_refresh_buffer
            if self._session_token is None or time.time() >= (
                self._session_expires_at - buffer
            ):
                self._discard_session(delete_remote=True)
                self._create_session()

    def refresh_session(self) -> None:
        """Manually refresh the session token."""
        with self._session_lock:
            self._discard_session(delete_remote=True)
            self._create_session()

    # Service accessors (lazy-loaded)

    @property
    def administrations(self) -> AdministrationService:
        """Administration service."""
        if self._administrations is None:
            self._administrations = AdministrationService(self)
        return self._administrations

    @property
    def cost_centers(self) -> CostCenterService:
        """Cost center service."""
        if self._cost_centers is None:
            self._cost_centers = CostCenterService(self)
        return self._cost_centers

    @property
    def email_templates(self) -> EmailTemplateService:
        """Email template service."""
        if self._email_templates is None:
            self._email_templates = EmailTemplateService(self)
        return self._email_templates

    @property
    def invoice_templates(self) -> InvoiceTemplateService:
        """Invoice template service."""
        if self._invoice_templates is None:
            self._invoice_templates = InvoiceTemplateService(self)
        return self._invoice_templates

    @property
    def invoices(self) -> InvoiceService:
        """Invoice service."""
        if self._invoices is None:
            self._invoices = InvoiceService(self)
        return self._invoices

    @property
    def ledgers(self) -> LedgerService:
        """Ledger service."""
        if self._ledgers is None:
            self._ledgers = LedgerService(self)
        return self._ledgers

    @property
    def members(self) -> MemberService:
        """Member service (only for clubs/associations)."""
        if self._members is None:
            self._members = MemberService(self)
        return self._members

    @property
    def mutations(self) -> MutationService:
        """Mutation service."""
        if self._mutations is None:
            self._mutations = MutationService(self)
        return self._mutations

    @property
    def products(self) -> ProductService:
        """Product service."""
        if self._products is None:
            self._products = ProductService(self)
        return self._products

    @property
    def relations(self) -> RelationService:
        """Relation service."""
        if self._relations is None:
            self._relations = RelationService(self)
        return self._relations

    @property
    def units(self) -> UnitService:
        """Unit service."""
        if self._units is None:
            self._units = UnitService(self)
        return self._units
