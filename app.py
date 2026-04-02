import io
import json
import base64
import os
import secrets

import pyotp
import qrcode

from flask import (Flask, render_template, redirect, url_for,
                   flash, session, abort, current_app)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from config import config
from models import db, User
from forms import RegisterForm, LoginForm, TOTPForm, SetupMFAForm

load_dotenv()

# ── Extension instances (uninitialised until create_app) ──────────────────────
login_manager = LoginManager()
mail          = Mail()
limiter       = Limiter(key_func=get_remote_address, default_limits=[])


# ══════════════════════════════════════════════════════════════════════════════
#  Helper functions
# ══════════════════════════════════════════════════════════════════════════════

# ── Email verification tokens ─────────────────────────────────────────────────

def _serializer():
    """Return a URL-safe timed serialiser using the app's SECRET_KEY."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def generate_token(email, salt='email-verification'):
    """Create a signed, expiring token that embeds the user's email."""
    return _serializer().dumps(email, salt=salt)


def verify_token(token, salt='email-verification', max_age=3600):
    """
    Decode and validate a token.  Returns the email on success, None on failure.
    max_age is in seconds (default 1 hour).
    """
    try:
        return _serializer().loads(token, salt=salt, max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None


# ── Email sending ─────────────────────────────────────────────────────────────

def send_verification_email(user):
    """
    Send (or in development: log) a verification email to the user.
    The link is always printed to the Flask console so you can test
    without SMTP credentials during development.
    """
    token      = generate_token(user.email)
    verify_url = url_for('verify_email', token=token, _external=True)

    # Always log the link so development works without an SMTP server.
    current_app.logger.info(
        f'\n{"=" * 60}\n'
        f'[DEV] VERIFICATION LINK for {user.email}:\n'
        f'{verify_url}\n'
        f'{"=" * 60}'
    )

    msg = Message(
        subject='Verify your Quiz App email',
        recipients=[user.email],
        html=render_template('verify_email_body.html', user=user, verify_url=verify_url),
    )
    mail.send(msg)


# ── Backup codes ──────────────────────────────────────────────────────────────

def generate_backup_codes():
    """
    Generate 8 random 8-character uppercase backup codes.
    Returns (plaintext_list, hashed_list).
    The plaintext list is shown to the user once; only hashes are stored.
    """
    codes  = [secrets.token_hex(4).upper() for _ in range(8)]
    hashed = [generate_password_hash(c, method='pbkdf2:sha256') for c in codes]
    return codes, hashed


def consume_backup_code(user, code):
    """
    Check whether `code` matches any stored backup-code hash.
    If it matches, that hash is deleted (each code is single-use).
    Returns True on a match, False otherwise.
    """
    if not user.backup_codes_json:
        return False
    hashes      = json.loads(user.backup_codes_json)
    code_upper  = code.strip().upper()
    for i, h in enumerate(hashes):
        if check_password_hash(h, code_upper):
            hashes.pop(i)
            user.backup_codes_json = json.dumps(hashes)
            db.session.commit()
            return True
    return False


# ── QR code ───────────────────────────────────────────────────────────────────

def make_qr_base64(uri):
    """Render a TOTP provisioning URI as a base64-encoded PNG (for inline <img>)."""
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()


# ══════════════════════════════════════════════════════════════════════════════
#  App factory
# ══════════════════════════════════════════════════════════════════════════════

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('APP_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    login_manager.login_view            = 'login'
    login_manager.login_message         = 'Please sign in to access the quiz.'
    login_manager.login_message_category = 'error'

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── 429 handler: show a friendly flash instead of a blank error page ──────
    @app.errorhandler(429)
    def too_many_requests(e):
        flash('Too many attempts. Please wait a moment and try again.', 'error')
        return redirect(url_for('welcome')), 429

    # ══════════════════════════════════════════════════════════════════════════
    #  Public routes
    # ══════════════════════════════════════════════════════════════════════════

    @app.route('/')
    def welcome():
        if current_user.is_authenticated:
            return redirect(url_for('quiz'))
        return render_template('welcome.html')

    # ── Register ───────────────────────────────────────────────────────────────

    @app.route('/register', methods=['GET', 'POST'])
    @limiter.limit('10 per minute')
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('quiz'))
        form = RegisterForm()
        if form.validate_on_submit():
            email = form.email.data.strip().lower()
            if User.query.filter_by(email=email).first():
                flash('An account with this email already exists.', 'error')
                return render_template('register.html', form=form)
            user = User(
                first_name    = form.first_name.data.strip(),
                last_name     = form.last_name.data.strip(),
                email         = email,
                password_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256'),
                is_verified   = False,
            )
            db.session.add(user)
            db.session.commit()
            send_verification_email(user)
            session['_verify_email'] = email
            return redirect(url_for('verify_pending'))
        return render_template('register.html', form=form)

    # ── Email verification ─────────────────────────────────────────────────────

    @app.route('/verify-pending')
    def verify_pending():
        email = session.get('_verify_email')
        if not email:
            return redirect(url_for('welcome'))
        return render_template('verify_pending.html', email=email)

    @app.route('/resend-verification')
    @limiter.limit('3 per hour')
    def resend_verification():
        email = session.get('_verify_email')
        if not email:
            return redirect(url_for('welcome'))
        user = User.query.filter_by(email=email, is_verified=False).first()
        if user:
            send_verification_email(user)
        # Always show success to avoid leaking whether the address exists.
        flash('Verification email resent. Check your inbox (and spam folder).', 'success')
        return redirect(url_for('verify_pending'))

    @app.route('/verify-email/<token>')
    def verify_email(token):
        email = verify_token(token)
        if not email:
            flash('The verification link is invalid or has expired. '
                  'Please request a new one.', 'error')
            return redirect(url_for('welcome'))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Account not found.', 'error')
            return redirect(url_for('welcome'))
        if user.is_verified:
            flash('Email already verified. Please sign in.', 'success')
            return redirect(url_for('login'))
        user.is_verified = True
        db.session.commit()
        session.pop('_verify_email', None)
        flash('Email verified! You can now sign in.', 'success')
        return redirect(url_for('login'))

    # ── Login ──────────────────────────────────────────────────────────────────

    @app.route('/login', methods=['GET', 'POST'])
    @limiter.limit('20 per minute')
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('quiz'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(
                email=form.email.data.strip().lower()
            ).first()

            # 1. Lockout check (before password work to fail fast)
            if user and user.is_locked():
                flash('Account temporarily locked after too many failed attempts. '
                      'Try again in 15 minutes.', 'error')
                return render_template('login.html', form=form)

            # 2. Credential check
            pw_ok = user and check_password_hash(user.password_hash, form.password.data)
            if not pw_ok:
                if user:
                    user.record_failed_login()
                flash('Incorrect email or password.', 'error')
                return render_template('login.html', form=form)

            # 3. Verified check
            if not user.is_verified:
                session['_verify_email'] = user.email
                flash('Please verify your email address before signing in. '
                      'Check your inbox for the verification link.', 'error')
                return redirect(url_for('verify_pending'))

            # 4. Successful credential check — clear lockout state
            user.reset_login_attempts()

            # 5. MFA check
            if user.totp_enabled:
                session['_mfa_pending']  = user.id
                session['_mfa_attempts'] = 0
                return redirect(url_for('mfa'))

            login_user(user)
            return redirect(url_for('quiz'))
        return render_template('login.html', form=form)

    # ── MFA challenge ──────────────────────────────────────────────────────────

    @app.route('/mfa', methods=['GET', 'POST'])
    @limiter.limit('20 per minute')
    def mfa():
        user_id = session.get('_mfa_pending')
        if not user_id:
            # No pending MFA — nothing to challenge
            return redirect(url_for('login'))

        user = db.session.get(User, user_id)
        if not user:
            session.pop('_mfa_pending', None)
            return redirect(url_for('login'))

        form = TOTPForm()
        if form.validate_on_submit():
            code       = form.code.data.strip()
            totp       = pyotp.TOTP(user.totp_secret)
            # valid_window=1 allows one 30-second window of clock skew
            totp_ok    = totp.verify(code, valid_window=1)
            backup_ok  = (not totp_ok) and consume_backup_code(user, code)

            if totp_ok or backup_ok:
                session.pop('_mfa_pending',  None)
                session.pop('_mfa_attempts', None)
                login_user(user)
                if backup_ok:
                    flash('Backup code used — it has been removed. '
                          'Visit Security settings to check your remaining codes.', 'success')
                return redirect(url_for('quiz'))

            # Failed attempt
            attempts = session.get('_mfa_attempts', 0) + 1
            session['_mfa_attempts'] = attempts
            if attempts >= 5:
                session.pop('_mfa_pending',  None)
                session.pop('_mfa_attempts', None)
                flash('Too many failed MFA attempts. Please sign in again.', 'error')
                return redirect(url_for('login'))

            flash(f'Invalid code — {5 - attempts} attempt(s) remaining.', 'error')

        return render_template('mfa.html', form=form)

    # ── Logout ─────────────────────────────────────────────────────────────────

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('welcome'))

    # ══════════════════════════════════════════════════════════════════════════
    #  Protected routes (require login)
    # ══════════════════════════════════════════════════════════════════════════

    @app.route('/quiz')
    @login_required
    def quiz():
        return render_template('quiz.html')

    # ── Security settings ──────────────────────────────────────────────────────

    @app.route('/security')
    @login_required
    def security():
        disable_form = TOTPForm()
        return render_template('security.html', disable_form=disable_form)

    # ── Set up TOTP ────────────────────────────────────────────────────────────

    @app.route('/setup-mfa', methods=['GET', 'POST'])
    @login_required
    def setup_mfa():
        if current_user.totp_enabled:
            flash('MFA is already enabled on your account.', 'error')
            return redirect(url_for('security'))

        # Generate a secret once per setup session.
        # Keeping it in session means page refreshes don't invalidate the QR code.
        if '_totp_setup' not in session:
            session['_totp_setup'] = pyotp.random_base32()

        secret = session['_totp_setup']
        totp   = pyotp.TOTP(secret)
        uri    = totp.provisioning_uri(
            name=current_user.email,
            issuer_name='Quiz App',
        )
        qr_b64 = make_qr_base64(uri)

        form = SetupMFAForm()
        if form.validate_on_submit():
            if not totp.verify(form.code.data.strip(), valid_window=1):
                flash('Incorrect code — make sure your authenticator app '
                      'is showing the latest 6-digit code.', 'error')
                return render_template('setup_mfa.html',
                                       form=form, qr_b64=qr_b64, secret=secret)

            # Code confirmed — save the secret and generate backup codes
            codes, hashed = generate_backup_codes()
            current_user.totp_secret       = secret
            current_user.totp_enabled      = True
            current_user.backup_codes_json = json.dumps(hashed)
            db.session.commit()

            session.pop('_totp_setup', None)
            # Store codes in session briefly so backup_codes page can display them
            session['_show_backup_codes'] = True
            session['_new_backup_codes']  = codes
            return redirect(url_for('backup_codes'))

        return render_template('setup_mfa.html', form=form, qr_b64=qr_b64, secret=secret)

    # ── Show backup codes (one-time) ───────────────────────────────────────────

    @app.route('/backup-codes')
    @login_required
    def backup_codes():
        # _show_backup_codes is set only immediately after setup — pop clears it
        if not session.pop('_show_backup_codes', False):
            abort(403)
        codes = session.pop('_new_backup_codes', [])
        return render_template('backup_codes.html', codes=codes)

    # ── Disable TOTP ───────────────────────────────────────────────────────────

    @app.route('/disable-mfa', methods=['POST'])
    @login_required
    @limiter.limit('10 per minute')
    def disable_mfa():
        if not current_user.totp_enabled:
            return redirect(url_for('security'))

        form = TOTPForm()
        if not form.validate_on_submit():
            flash('Invalid request.', 'error')
            return redirect(url_for('security'))

        code      = form.code.data.strip()
        totp      = pyotp.TOTP(current_user.totp_secret)
        code_ok   = totp.verify(code, valid_window=1) or consume_backup_code(current_user, code)

        if not code_ok:
            flash('Invalid code — MFA was not disabled.', 'error')
            return redirect(url_for('security'))

        current_user.totp_secret       = None
        current_user.totp_enabled      = False
        current_user.backup_codes_json = None
        db.session.commit()
        flash('MFA has been disabled.', 'success')
        return redirect(url_for('security'))

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
