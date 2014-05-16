DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "memory"
    }
}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "polymorphic",
    "elasticutils",
    "elastimorphic",
    "elastimorphic.tests.testapp",
)

ES_URLS = ["http://127.0.0.1:9200"]

SECRET_KEY = "EVERYBODY_DANCE_NOW"
