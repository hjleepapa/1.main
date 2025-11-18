import logging
import os
import uuid
from typing import Any, Dict, Optional

import jwt
from jwt import PyJWKClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from convonet.models.user_models import User, Team, TeamMembership

logger = logging.getLogger(__name__)


def _coerce_uuid(value: Optional[str]) -> Optional[uuid.UUID]:
    if not value:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return None


class FronteggAuthManager:
    """
    Handles FrontMCP (Frontegg) token validation and optional local user syncing.
    This follows the setup steps from the official integration guide:
    https://portal.frontegg.com/development/frontegg-integration-guide
    """

    def __init__(self):
        self.base_url = os.getenv("FRONTEGG_BASE_URL")
        self.audience = os.getenv("FRONTEGG_AUDIENCE") or os.getenv("FRONTEGG_CLIENT_ID")
        self.issuer = os.getenv("FRONTEGG_ISSUER") or self.base_url
        self.jwks_url = (
            os.getenv("FRONTEGG_JWKS_URL")
            or f"{self.base_url.rstrip('/')}/.well-known/jwks.json"
            if self.base_url
            else None
        )
        self.default_team_id = _coerce_uuid(os.getenv("FRONTEGG_DEFAULT_TEAM_ID"))
        self.enabled = bool(self.base_url and self.jwks_url and self.audience and self.issuer)

        self._jwk_client = PyJWKClient(self.jwks_url) if self.enabled else None

        db_uri = os.getenv("DB_URI")
        self._session_local = None
        if db_uri:
            engine = create_engine(db_uri)
            self._session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a Frontegg-issued JWT via JWKS."""
        if not (self.enabled and self._jwk_client):
            return None
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
            payload["_provider"] = "frontegg"
            return payload
        except Exception as exc:
            logger.warning("Frontegg token validation failed: %s", exc)
            return None

    def build_request_user(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        """Create the Flask request.current_user payload for Frontegg identities."""
        local_user = self._sync_local_user(claims) if self._session_local else None
        team_id = self._resolve_team_id(local_user)
        return {
            "user_id": str(local_user.id) if local_user else claims.get("sub"),
            "email": claims.get("email"),
            "roles": self._extract_roles(claims),
            "team_id": team_id,
            "frontegg_tenant_id": claims.get("tenantId"),
        }

    def _extract_roles(self, claims: Dict[str, Any]) -> list:
        if "roles" in claims and isinstance(claims["roles"], list):
            return claims["roles"]
        if "permissions" in claims and isinstance(claims["permissions"], list):
            return claims["permissions"]
        return ["user"]

    def _sync_local_user(self, claims: Dict[str, Any]) -> Optional[User]:
        """Ensure there is a local users_convonet entry for the Frontegg identity."""
        email = claims.get("email")
        if not email:
            return None

        first_name = claims.get("given_name") or email.split("@")[0]
        last_name = claims.get("family_name") or "User"
        preferred_username = claims.get("preferred_username") or email.split("@")[0]

        with self._session_local() as session:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                username = self._ensure_unique_username(session, preferred_username)
                user = User(
                    email=email,
                    username=username,
                    password_hash="FRONTEGG_SSO_USER",
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True,
                    is_verified=True,
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info("Created local user from Frontegg identity: %s", email)

            if self.default_team_id:
                self._ensure_membership(session, user)

            return user

    def _ensure_unique_username(self, session, base_username: str) -> str:
        candidate = base_username
        counter = 1
        while session.query(User).filter(User.username == candidate).first():
            candidate = f"{base_username}-{counter}"
            counter += 1
        return candidate

    def _ensure_membership(self, session, user: User):
        """Attach the user to the default hackathon team if configured."""
        existing = (
            session.query(TeamMembership)
            .filter(
                TeamMembership.user_id == user.id,
                TeamMembership.team_id == self.default_team_id,
            )
            .first()
        )
        if existing:
            return

        team = session.query(Team).filter(Team.id == self.default_team_id).first()
        if not team:
            logger.warning(
                "FRONTEGG_DEFAULT_TEAM_ID is set, but no matching team exists in DB."
            )
            return

        membership = TeamMembership(user_id=user.id, team_id=team.id, role="member")
        session.add(membership)
        session.commit()
        logger.info("Attached %s to default team %s via Frontegg SSO", user.email, team.name)

    def _resolve_team_id(self, user: Optional[User]) -> Optional[str]:
        if not user or not self._session_local:
            return str(self.default_team_id) if self.default_team_id else None
        with self._session_local() as session:
            membership = (
                session.query(TeamMembership)
                .filter(TeamMembership.user_id == user.id)
                .order_by(TeamMembership.joined_at.asc())
                .first()
            )
            if membership:
                return str(membership.team_id)
        return str(self.default_team_id) if self.default_team_id else None


def _build_manager() -> Optional[FronteggAuthManager]:
    manager = FronteggAuthManager()
    return manager if manager.enabled else None


frontegg_auth_manager = _build_manager()


