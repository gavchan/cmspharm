from django.db import models

class AuditLog(models.Model):
    """
    Maps to CMS table: audit_log
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField()
    actor = models.CharField(max_length=255, blank=True, null=True)
    class_name = models.CharField(max_length=255)
    date_created = models.DateTimeField()
    event_name = models.CharField(max_length=255)
    last_updated = models.DateTimeField()
    new_value = models.TextField(blank=True, null=True)
    old_value = models.TextField(blank=True, null=True)
    persisted_object_id = models.CharField(max_length=255, blank=True, null=True)
    persisted_object_version = models.CharField(max_length=255, blank=True, null=True)
    property_name = models.CharField(max_length=255, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'audit_log'
        app_label = 'cmssys'

class CmsUser(models.Model):
    """
    Maps to CMS table: user
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField()
    active = models.BooleanField()
    cname = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField()
    email = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField()
    medical_council_reg_no = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255)
    tel = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    user_profile = models.ForeignKey('UserProfile', on_delete=models.PROTECT, db_column='user_profile_id')
    username = models.CharField(unique=True, max_length=255)
    ehr_uid = models.CharField(max_length=255, blank=True, null=True)
    priority = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
        app_label = 'cmssys'
    
    def __str__(self):
        return '{}|{} ({})'.format(
            self.id, self.username, self.name
        )

class UserProfile(models.Model):
    """
    Maps to CMS table user_profile
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'user_profile'
        app_label = 'cmssys'
