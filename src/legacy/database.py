class Router:
    """
    A router to control all database operations on models in the
    legacy application.
    """
    def db_for_read(self, model, **hints):
        """Attempts to read legacy models go to core."""

        if model._meta.app_label == 'legacy':
            return 'core'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Make sure the legacy app only appears in the 'core' database."""

        if app_label == 'legacy':
            return db == 'core'
        return None
