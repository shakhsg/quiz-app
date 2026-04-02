from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Lock account for this many minutes after too many failures
_LOCKOUT_MINUTES   = 15
_LOCKOUT_THRESHOLD = 5


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id                = db.Column(db.Integer, primary_key=True)
    first_name        = db.Column(db.String(50),  nullable=False)
    last_name         = db.Column(db.String(50),  nullable=False)
    email             = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash     = db.Column(db.String(256), nullable=False)

    # ── Email verification ────────────────────────────────────────────────────
    is_verified       = db.Column(db.Boolean, default=False, nullable=False)

    # ── TOTP MFA ──────────────────────────────────────────────────────────────
    totp_secret       = db.Column(db.String(64),  nullable=True)
    totp_enabled      = db.Column(db.Boolean, default=False, nullable=False)
    # JSON list of Werkzeug-hashed backup codes; each consumed code is removed.
    backup_codes_json = db.Column(db.Text, nullable=True)

    # ── Brute-force lockout ───────────────────────────────────────────────────
    failed_logins     = db.Column(db.Integer, default=0, nullable=False)
    locked_until      = db.Column(db.DateTime, nullable=True)

    # ── Computed properties ───────────────────────────────────────────────────

    @property
    def initials(self):
        return (self.first_name[0] + self.last_name[0]).upper()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    # ── Lockout helpers ───────────────────────────────────────────────────────

    def is_locked(self):
        """Return True if the account is currently under a temporary lockout."""
        return bool(self.locked_until and self.locked_until > datetime.utcnow())

    def record_failed_login(self):
        """
        Increment the failure counter.
        Locks the account for _LOCKOUT_MINUTES after _LOCKOUT_THRESHOLD failures.
        """
        self.failed_logins = (self.failed_logins or 0) + 1
        if self.failed_logins >= _LOCKOUT_THRESHOLD:
            self.locked_until = datetime.utcnow() + timedelta(minutes=_LOCKOUT_MINUTES)
        db.session.commit()

    def reset_login_attempts(self):
        """Call on a successful login to clear the failure counter and lockout."""
        self.failed_logins = 0
        self.locked_until  = None
        db.session.commit()

    @property
    def backup_codes_count(self):
        """Return the number of remaining (unused) backup codes."""
        if not self.backup_codes_json:
            return 0
        import json
        return len(json.loads(self.backup_codes_json))
