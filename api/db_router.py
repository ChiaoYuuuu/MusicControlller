class OracleRouter:
    def db_for_read(self, model, **hints):
        if model._meta.model_name == 'topcharts':
            return 'oracle'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.model_name == 'topcharts':
            return 'oracle'
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == 'topcharts':
            return db == 'oracle'
        return db == 'default'

