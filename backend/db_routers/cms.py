class CmsDbRouter:
    """
    A router to control all database operations on models in the
    user application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read cms models go to cms_db.
        """
        if model._meta.app_label == 'cmsinv' or model._meta.app_label == 'cmssys':
            return 'cms_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write cms models to cms_db
        """
        if model._meta.app_label == 'cmsinv' or model._meta.app_label == 'cmssys':
            return 'cms_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Do not allow relations involving the cms_db
        """
        if (obj1._meta.app_label == 'cmsinv' or obj2._meta.app_label == 'cmsinv'):
            return False
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Do not allow migration of models relating to the cms_db
        """
        if app_label == 'cmsinv':
            return False
        return True