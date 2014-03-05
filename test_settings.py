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

ES_URLS = ["http://192.168.33.101:9200"]

SECRET_KEY = "EVERYBODY_DANCE_NOW"
