from django.db import models

# Custom Field Definitions
class MySQLBitBooleanField(models.BooleanField):
    """
    Custom field definition to cater for MySQL bit field
    Adapted from https://github.com/adamchainz/django-mysql
    Note:
    - Wanted to use django-mysql's Bit1BooleanField but ran into error even though none was knowingly defined: 
      MySQLdb._exceptions.OperationalError: (1193, "Unknown system variable 'innodb_strict_mode'")
    """
    def db_type(self, connection):
        return "bit(1)"

    def from_db_value(self, value, expression, connection):
        if isinstance(value, bytes):
            value = value == b"\x01"
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        else:
            return 1 if value else 0

class TextBooleanField(models.BooleanField):
    """
    Custom field created to model a boolean type field that has been formatted as "TEXT"
    in the CMS MySQL database
    Used by: cmsinv.InventoryItem
    """
    def db_type(self, connection):
        return "boolean like text"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value 
        elif value is "1":
            return True
        else:
            return False
        
    def get_prep_value(self, value):
        if value is None:
            return value
        else:
            return 1 if value else 0

class AuditLog(models.Model):
    """
    Maps to CMS table: audit_log
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    actor = models.CharField(max_length=255, blank=True, null=True)
    class_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    event_name = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)
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
        ordering = ['-last_updated']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('drugdb.views.details', args=[str(self.id)])

    def __str__(self):
        return f"{self.date_created} [{self.actor}] {self.event_name} {self.class_name}: {self.property_name} - {self.old_value} => {self.new_value}"
  
class CmsUser(models.Model):
    """
    Maps to CMS table: user
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    active = models.BooleanField(default=True)
    cname = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
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
        ordering = ['id']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cmssys.views.details', args=[str(self.id)])

    def __str__(self):
        return f"{self.id} | {self.name} [{self.username}]"

class UserProfile(models.Model):
    """
    Maps to CMS table user_profile
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'user_profile'
        app_label = 'cmssys'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cmssys.views.details', args=[str(self.id)])

    def __str__(self):
        return f"{self.id} | ver.{self.version}"

class Patient(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField()
    active = models.TextField()  # This field type is a guess.
    address_id = models.BigIntegerField(blank=True, null=True)
    alias1 = models.CharField(max_length=255, blank=True, null=True)
    alias2 = models.CharField(max_length=255, blank=True, null=True)
    chinese_given_name = models.CharField(max_length=255, blank=True, null=True)
    chinese_sur_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField()
    dob = models.DateTimeField(blank=True, null=True)
    dob_inexact = models.TextField()  # This field type is a guess.
    email = models.CharField(max_length=255, blank=True, null=True)
    epr = models.TextField()  # This field type is a guess.
    fax = models.CharField(max_length=255, blank=True, null=True)
    given_name = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.BigIntegerField(blank=True, null=True)
    last_updated = models.DateTimeField()
    medical_background_id = models.BigIntegerField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
    nextofkin1_id = models.BigIntegerField(blank=True, null=True)
    nextofkin2_id = models.BigIntegerField(blank=True, null=True)
    official_id = models.CharField(max_length=255, blank=True, null=True)
    official_id_type_id = models.BigIntegerField()
    pager = models.CharField(max_length=255, blank=True, null=True)
    patient_no = models.CharField(unique=True, max_length=255, blank=True, null=True)
    referrer_id = models.BigIntegerField(blank=True, null=True)
    register_clinic = models.CharField(max_length=255, blank=True, null=True)
    responsible_doctor_id = models.BigIntegerField(blank=True, null=True)
    security = models.TextField()  # This field type is a guess.
    sex_id = models.BigIntegerField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    sur_name = models.CharField(max_length=255, blank=True, null=True)
    tel_home = models.CharField(max_length=255, blank=True, null=True)
    tel_mobile = models.CharField(max_length=255, blank=True, null=True)
    tel_office = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    address_work_id = models.BigIntegerField(blank=True, null=True)
    doi = models.DateTimeField(blank=True, null=True)
    patient_address = models.CharField(max_length=255, blank=True, null=True)
    patient_type_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'patient'
        
    @property
    def initials(self):
        name_initials = self.sur_name[0].upper()
        if self.given_name:
            given_names = self.given_name.split(' ')
        if len(given_names) > 0:
            for name in given_names:
                name_initials += name[0].upper()
        return name_initials

class EncounterType(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField()
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'encounter_type'

    def __str__(self):
        return f"{self.id} | label={self.label}; value={self.value}"


class Encounter(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField()
    # bill_id = models.BigIntegerField()
    consultation_notes_id = models.BigIntegerField(blank=True, null=True)
    date_created = models.DateTimeField()
    doctor = models.ForeignKey(
        CmsUser, on_delete=models.PROTECT,
        db_column='doctor_id',
    )
    last_updated = models.DateTimeField()
    # patient_id = models.BigIntegerField()
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT,
        db_column='patient_id',
    )
    prescription_id = models.BigIntegerField(blank=True, null=True)
    encounter_type = models.ForeignKey(
        EncounterType, on_delete=models.PROTECT,
        db_column='type_id',
    )
    vital_sign_id = models.BigIntegerField(blank=True, null=True)
    consumable_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'encounter'

    def __str__(self):
        return f"{self.date_created} | Doctor: {self.doctor};  ${self.encounter_type}"

