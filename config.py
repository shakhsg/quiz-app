import os


class Config:
    SECRET_KEY             = os.environ.get('SECRET_KEY', 'dev-only-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED       = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Flask-Mail
    MAIL_SERVER         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS        = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'Quiz App <noreply@quizapp.com>')


class DevelopmentConfig(Config):
    DEBUG                = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz.db'
    SESSION_COOKIE_SECURE = False
    # Suppresses actual sending; the link is printed to the Flask console instead.
    MAIL_SUPPRESS_SEND   = True


class ProductionConfig(Config):
    DEBUG                = False
    SESSION_COOKIE_SECURE = True
    MAIL_SUPPRESS_SEND   = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///quiz.db').replace(
        'postgres://', 'postgresql://', 1
    )


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
