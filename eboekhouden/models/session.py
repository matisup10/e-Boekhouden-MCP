"""Session models for the e-Boekhouden SDK."""

from __future__ import annotations

from eboekhouden.models.base import EBoekhoudenModel


class SessionRequest(EBoekhoudenModel):
    """Request body for creating a session."""

    access_token: str
    source: str


class SessionResponse(EBoekhoudenModel):
    """Response from creating a session."""

    token: str
    expires_in: int
