from django.db import models
from cmssys.models import CMSModel, CmsUser, TextBooleanField 

# CMS INVENTORY/DRUGS Models

class Supplier(CMSModel):
    """
    Maps to CMS table: supplier_manufacturer
    Stores supplier/cert holder/manufacturer contact details
    """
    CERT_HOLDER = 'Certificate Holder'
    SUPPLIER = 'Supplier'
    MANUFACTURER = 'Manufacturer'
    SUPP_TYPE_CHOICES = [
        (CERT_HOLDER, 'Certificate Holder'),
        (SUPPLIER, 'Supplier'),
        (MANUFACTURER, 'Manufacturer'),
    ]

    version = models.BigIntegerField(default=0)
    address = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    tel_home = models.CharField(max_length=255, blank=True, null=True)
    tel_mobile = models.CharField(max_length=255, blank=True, null=True)
    tel_office = models.CharField(max_length=255, blank=True, null=True)
    supp_type = models.CharField(db_column='type', choices=SUPP_TYPE_CHOICES, max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'supplier_manufacturer'
        app_label = 'cmsinv'
        ordering = ['name']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cmsinv.views.details', args=[str(self.id)])

    def __str__(self):
        return f"{self.name}"

class Advisory(CMSModel):
    """
    Maps to CMS table: advisory
    Stores drug advisory information
    """

    version = models.BigIntegerField(default=0)
    alias = models.CharField(unique=True, max_length=255)
    created_by = models.ForeignKey(
        'cmssys.CmsUser', on_delete=models.PROTECT, 
        db_column='created_by_id', blank=True, null=True
        )
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    description_chinese = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'advisory'
        app_label = 'cmsinv'
        verbose_name_plural = 'Advisory list'


    def __str__(self):
        return f"{self.alias} | {self.description_chinese} / {self.description}"

class Instruction(CMSModel):
    """
    Maps to CMS table: instruction
    Stores medication instructions
    """

    version = models.BigIntegerField(default=0)
    alias = models.CharField(unique=True, max_length=255)
    created_by = models.ForeignKey(
        'cmssys.CmsUser', on_delete=models.PROTECT, 
        db_column='created_by_id', blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    description_chinese = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'instruction'
        app_label = 'cmsinv'

    def __str__(self):
        return f"{self.alias} | {self.description_chinese} / {self.description}"

class InventoryItemType(CMSModel):
    """
    Maps to CMS table: inventory_item_type
    Stores inventory type, note that only type 1=Drug is used in the CMS app
    """

    version = models.BigIntegerField(default=0)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'inventory_item_type'
        app_label = 'cmsinv'

    def __str__(self):
        return f"{self.id} | {self.name}"


class InventoryItem(CMSModel):
    """
    Maps to CMS table: inventory_item
    Stores details in inventory items, including current stock quantity
    """
    AMPOULE = 'AMPOULE'
    BOTTLE = 'BOTTLE'
    BOX = 'BOX'
    CAPSULE = 'CAP'
    DOSE = 'DOSE'
    GRAM = 'GRAM'
    INJECTION = 'INJECTION'
    MG = 'MG'
    ML = 'ML'
    PACK = 'PACK'
    TAB = 'TAB'
    TUBE = 'TUBE'
    UNIT = 'UNIT'
    VIAL = 'VIAL'

    ITEMS_UNIT_CHOICES = [
        (AMPOULE, 'Ampoule'),
        (BOTTLE, 'Bottle'),
        (BOX, 'Box'),
        (CAPSULE, 'Cap'),
        (DOSE, 'Dose'),
        (GRAM, 'gram'),
        (INJECTION, 'Injection'),
        (MG, 'mg'),
        (ML, 'mL'),
        (PACK, 'Pack'),
        (TAB, 'Tablet'),
        (TUBE, 'Tube'),
        (UNIT, 'Unit'),
        (VIAL, 'Vial'),
    ]

    version = models.BigIntegerField(default=0)
    advisory = models.ForeignKey(
        'Advisory', on_delete=models.PROTECT, 
        db_column='advisory_id', blank=True, null=True)
    
    alias = models.CharField(max_length=255, blank=True, null=True)
    avg_cost = models.FloatField(default=0)
    category = models.CharField(max_length=255, blank=True, null=True)

    # certificate_holder - CMS database accepts 'Supplier' or 'Certificate Holder' but not 'Manufacturer' 
    # in this field, need to add validation to enforce this
    certificate_holder = models.ForeignKey(
        'Supplier', on_delete=models.CASCADE, 
        db_column='certificate_holder_id'
        )
    clinic_drug_no = models.CharField(max_length=255, blank=True, null=True, unique=True)
    dangerous_sign = TextBooleanField(default=False)  # MySQL text field, behaves like Boolean
    date_created = models.DateTimeField(auto_now_add=True)
    discontinue = TextBooleanField()  # MySQL text field, behaves like Boolean
    dosage = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=255, blank=True, null=True)
    expected_qty = models.FloatField(default=1000)
    expire_date = models.DateField(blank=True, null=True)
    frequency = models.CharField(max_length=255, blank=True, null=True)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    generic_name_chinese = models.CharField(max_length=255, blank=True, null=True)
    ingredient = models.TextField(blank=True, null=True)
    instruction = models.ForeignKey(
        'Instruction', on_delete=models.PROTECT, 
        db_column='instruction_id', 
        blank=True, null=True
        )

    # N.B. inventory_type is not ever used in CMS App - by default all are set to Null
    # To make use of this, to set as:
    # - "Drug": Registered Drug (reg_no)
    # - "Supplement": Health supplement and vitamins
    # - "Nutrition": Nutritional supplement, e.g. Ensure
    DRUG = 'Drug'
    SUPP = 'Supplement'
    INVENTORY_TYPE_CHOICES = [
        (DRUG, 'Drug'),         # Registered Drug
        (SUPP, 'Supplement'),   # Health supplements, vitamins, etc.
    ]

    inventory_type = models.CharField(choices=INVENTORY_TYPE_CHOICES, max_length=255, blank=True, null=True)
    is_clinic_drug_list = TextBooleanField()  # MySQL text field, behaves like Boolean
    is_master_drug_list = TextBooleanField()  # MySQL text field, behaves like Boolean
    label_name = models.CharField(max_length=255, blank=True, null=True)
    label_name_chinese = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    mini_dispensary_unit = models.FloatField(default=0)
    mini_dosage_unit = models.FloatField(default=0)
    product_name = models.CharField(max_length=255, blank=True, null=True) # CMS product_name is not unique
    product_name_chinese = models.CharField(max_length=255, blank=True, null=True)
    registration_no = models.CharField(unique=True, max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    reorder_level = models.FloatField(default=100)
    reorder_status = models.CharField(max_length=255, blank=True, null=True)
    standard_cost = models.FloatField(default=0)
    stock_qty = models.FloatField(default=0)
    unit = models.CharField(max_length=255, choices=ITEMS_UNIT_CHOICES, blank=True, null=True)
    unit_price = models.FloatField(default=0)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    priority = models.FloatField(default=0, blank=True, null=True)

    # inventory_item_type / type_id - Only type_id=1 (Drug) is ever used in the CMS App
    inventory_item_type = models.ForeignKey(
        'InventoryItemType', on_delete=models.PROTECT, 
        db_column='type_id')

    @property
    def is_active(self):
        return not(self.discontinue)

    @classmethod
    def generateNextClinicDrugNo(cls):
        """
        Generate new clinic drug no.
        """
        PREFIX = 'CN'
        DIGIT_LENGTH = 6
        clinic_drugs = cls.objects.filter(
            clinic_drug_no__isnull=False,
        ).exclude(clinic_drug_no__exact='')
        clinic_drug_nos = list(clinic_drugs.values_list('clinic_drug_no', flat=True).order_by('clinic_drug_no'))
        last_clinic_drug_no = clinic_drug_nos[-1]
        no_numeric = last_clinic_drug_no[len(PREFIX):]
        if len(no_numeric) != DIGIT_LENGTH:
            print('Warning: clinic_drug_no digits does not match configured.')
        next_no = str(int(no_numeric) + 1)
        next_clinic_drug_no = f"{PREFIX}{next_no.rjust(DIGIT_LENGTH, '0')}"
        # print(f"Last clinic drug no.: {last_clinic_drug_no}; Generated next no.: {next_clinic_drug_no}")

        return(next_clinic_drug_no)


    class Meta:
        managed = False
        db_table = 'inventory_item'
        app_label = 'cmsinv'

    def __str__(self):
        return f"{self.registration_no} | {self.product_name} / {self.generic_name} [{self.alias}]"

class InventoryItemSupplier(CMSModel):
    """
    Maps to CMS table: inventory_item_supplier_manufacturer
    Stores which inventory_items are supplied by which supplier_manufacturer

    CMS table inventory_item_supplier_manufacturer is a legacy table using a composite key as the primary key
    Django does not support composite keys and a many-to-many field could not be used for this table
    Workaround:
    - The legacy database was modified to add an autoincrement `id` primary key
    - see backend/scripts/alter-cmsdb-generate-id-from-composite-key.py
    """
 
    inventory_item = models.ForeignKey(
        'InventoryItem', on_delete=models.CASCADE,
        db_column='inventory_item_suppliers_id'
        )
    supplier = models.ForeignKey(
        'Supplier', on_delete=models.CASCADE,
        db_column='supplier_manufacturer_id'
        )
    suppliers_idx = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'inventory_item_supplier_manufacturer'
        app_label = 'cmsinv'

    def __str__(self):
        return f"{self.supplier.name} - {self.suppliers_idx} : {self.inventory_item.product_name}"

class InventoryMovementLog(CMSModel):
    """
    Maps to CMS table: inventory_movement_log
    Stores movement of inventory drugs (no other type of inventory utilized in CMS app)
    """
    DELIVERY = 'Delivery'
    DISPENSARY = 'Dispensary'
    RECONCILIATION = 'Reconciliation'
    STOCK_INIT = 'Stock Initialization'
    MOVEMENT_TYPE_CHOICES = [
        (DELIVERY, 'Delivery'),
        (DISPENSARY, 'Dispensary'),
        (RECONCILIATION, 'Reconciliation'),
        (STOCK_INIT, 'Stock Initialization'),
    ]

    version = models.BigIntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    lot_no = models.CharField(max_length=255, blank=True, null=True) # Not used in CMS - NULL
    move_item = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.FloatField()

    # reference_no - maps to table based on movement_type:
    #   Delivery => delivery
    #   Dispensary => consultation_notes_id (<= encounter)
    #   Reconciliation => depletion
    #   Stock Initialization => null - N.B.What transaction registers this?
    reference_no = models.CharField(max_length=255, blank=True, null=True)
    movement_type = models.CharField(db_column='type', choices=MOVEMENT_TYPE_CHOICES, max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inventory_movement_log'
        app_label = 'cmsinv'

    def __str__(self):
        return f"{self.last_updated} [{self.movement_type}]: {self.quantity} | {self.move_item}"

# CMS INVENTORY > REQUEST Models

class Request(CMSModel):
    """
    Maps to CMS table: request
    Stores inventory drug order requests
    """
    COMPLETED = 'Completed'
    PENDING = 'Pending'
    STATUS_CHOICES = [
        (COMPLETED, 'Completed'),
        (PENDING, 'Pending'),
    ]

    version = models.BigIntegerField(default=1)
    create_date = models.DateField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # remarks - New Request remarks textbox
    remarks = models.TextField(blank=True, null=True)
    requested_by = models.ForeignKey(
        'cmssys.CmsUser', on_delete=models.PROTECT,
        db_column='requested_by_id'
        )
    # settle_date - appears not to be used by CMS app
    settle_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    # status - toggled by "Completed" button, stored as text by CMS app
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, blank=True, null=True)
    supplier = models.ForeignKey(
        'Supplier', on_delete=models.PROTECT,
        db_column='supplier_id'
        )
    total_cost = models.FloatField()
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'request'
        app_label = 'cmsinv'

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('', kwargs={'pk': self.pk})
    def __str__(self):
        return f"{self.create_date} | [{self.status}] {self.requested_by.name} request to {self.supplier.name}"

class RequestItem(CMSModel):
    """
    Maps to CMS table: request_item
    """

    version = models.BigIntegerField(default=1)
    expected_qty = models.FloatField()
    item = models.ForeignKey(
        'InventoryItem', on_delete=models.PROTECT,
        db_column='item_id',
        )
    quantity = models.FloatField()
    remarks = models.TextField(blank=True, null=True)
    request = models.ForeignKey(
        'Request', on_delete=models.PROTECT, 
        db_column='request_id',
        )
    stock_qty = models.FloatField()
    unit = models.CharField(max_length=255, blank=True, null=True)
    request_items_idx = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'request_item'
        app_label = 'cmsinv'

    def __str__(self):
        return f"{self.request.create_date} | Request #{self.request.id}.{self.request_items_idx}: {self.quantity} x {self.item.product_name} ({self.request.status})"

# CMS INVENTORY > DELIVERY Models

class Delivery(CMSModel):
    """Maps to CMS table delivery"""
    """Stores delivery settlement details"""


    version = models.BigIntegerField(default=1)

    # cash_amount - amount to be deducted from CMS cash_book
    cash_amount = models.FloatField()
    create_date = models.DateField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    received_by = models.ForeignKey(
        'cmssys.CmsUser', on_delete=models.PROTECT, 
        db_column='received_by_id'
        )
    remarks = models.TextField(blank=True, null=True)

    # settle_date - not used in CMS app
    settle_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True) # Not used?
    supplier = models.ForeignKey(
        'Supplier', on_delete=models.PROTECT, 
        db_column='supplier_id'
        )
    # supplierdn - not used in CMS app, to use here for supplier invoice no.
    supplierdn = models.CharField(max_length=255, blank=True, null=True)
    total_cost = models.FloatField() # Not used?
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    delivery_note_no = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'delivery'
        app_label = 'cmsinv'
        verbose_name_plural = 'Deliveries'
    
    def __str__(self):
        return '{}| Paid ${:>6}; Received from {}'.format(
            self.create_date, self.cash_amount, self.supplier,
        )

class ReceivedItem(CMSModel):
    """
    Maps to CMS table: received_item
    """

    version = models.BigIntegerField(default=0)
    arrive_date = models.DateField(blank=True, null=True)
    cost = models.FloatField()
    dangerous_sign = TextBooleanField()
    delivery = models.ForeignKey(
        'Delivery', on_delete=models.CASCADE, 
        db_column='delivery_id'
        )
    drug_item = models.ForeignKey(
        'InventoryItem', on_delete=models.PROTECT,
        db_column='drug_item_id'
        )
    expire_date = models.DateTimeField(blank=True, null=True)
    lot_no = models.CharField(max_length=255)
    manufacturer_id = models.BigIntegerField(blank=True, null=True)
    quantity = models.FloatField()
    remarks = models.TextField(blank=True, null=True)

    # supplier_id - not used in CMS app
    supplier_id = models.BigIntegerField(blank=True, null=True)

    unit = models.CharField(max_length=255, blank=True, null=True)
    use_up = TextBooleanField(default=False)

    # received_items_idx - Index of item(s) in the delivery episode
    received_items_idx = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'received_item'
        app_label = 'cmsinv'

    def __str__(self):
        return '{}|Delivery #{}, Drug #{}'.format(
            self.arrive_date, self.delivery, self.drug_item
        )

# CMS INVENTORY > RECONCILIATION Model

class DepletionItem(CMSModel):

    version = models.BigIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    drug = models.ForeignKey(
        'InventoryItem', on_delete=models.PROTECT, 
        db_column='drug_id'
        )
    last_updated = models.DateTimeField(auto_now=True)
    quantity = models.FloatField()
    remark = models.TextField(blank=True, null=True)
    update_reason = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'depletion_item'
        app_label = 'cmsinv'

    def __str__(self):
        return '{}|{} x {} ({})'.format(
            self.date_created, self.quantity, self.drug, self.update_reason
        )

class Depletion(CMSModel):
    """Maps to CMS table: depletion"""
    """Stores inventory depletion info"""

    STOCKMOVE = 'Stock Move' # Stock move transaction
    STOCKTAKE = 'Stock Take' # Reconciliation transaction
    DEPLETION_TYPE_CHOICES = [
        (STOCKMOVE, 'Stock Move'),
        (STOCKTAKE, 'Stock Take')
    ]


    version = models.BigIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    # move_to - seems not used in CMS app
    move_to = models.TextField(blank=True, null=True)
    # remarks - Reconciliation model Remarks Text Box
    remarks = models.TextField(blank=True, null=True)
    depletion_type = models.CharField(choices=DEPLETION_TYPE_CHOICES, db_column='type', max_length=255)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'depletion'
        app_label = 'cmsinv'

    def __str__(self):
        return '{} | #{} - {}: {}'.format(
            self.id, self.depletion_type, self.remarks, self.last_updated
        )

class DepletionDepletionItem(CMSModel):
    """
    CMS table depletion_depletion_items is a legacy table using a composite key as the primary key
    Django does not support composite keys and a many-to-many field could not be used for this table
    Workaround:
    - The legacy database was modified to add an autoincrement `id` primary key
    - see backend/scripts/alter-cmsdb-generate-id-from-composite-key.py
    """
    depletion = models.ForeignKey(
        Depletion, on_delete=models.CASCADE,
        db_column='depletion_items_id'
        )
    depletion_item = models.ForeignKey(
        DepletionItem, on_delete=models.CASCADE,
        db_column='depletion_item_id'
    )
    items_idx = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'depletion_depletion_item'
        app_label = 'cmsinv'

    def __str__(self):
        return '{} [{}] {}'.format(
            self.depletion, self.items_idx, self.depletion_item
        )


# CMS PRESCRIPTION Models
#
# Prescription.id referenced in InventoryMovementLog (Dispensary)
# Prescription.id referenced in PrescriptionDetail, which could be used to locate InventoryItem.id
# 
class Prescription(CMSModel):

    version = models.BigIntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    encounter_id = models.BigIntegerField(blank=True, null=True)
    language_id = models.BigIntegerField(blank=True, null=True) # Default=NULL; not used in CMS
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prescription'
        app_label = 'cmsinv'
 

class PrescriptionDetail(CMSModel):

    version = models.BigIntegerField(default=0)
    advisory = models.ForeignKey(
        Advisory, on_delete=models.PROTECT,
        db_column='advisory_id', blank=True, null=True
    )
    
    dangerous_sign = TextBooleanField()  # MySQL text field, behaves like Boolean
    dosage = models.CharField(max_length=255)
    drug = models.ForeignKey(
        InventoryItem, on_delete=models.PROTECT,
        db_column='drug_id'
    )
    duration = models.CharField(max_length=255)
    filled_in_clinic = TextBooleanField()  # This field type is a guess.
    frequency = models.CharField(max_length=255)
    instruction = models.ForeignKey(
        Instruction, on_delete=models.PROTECT,
        db_column='instruction_id', blank=True, null=True
    )
    prescription = models.ForeignKey(
        Prescription, on_delete=models.PROTECT,
        db_column='prescription_id'
    )
    quantity = models.FloatField()
    remark = models.TextField(blank=True, null=True)
    status_print = models.IntegerField()
    total_cost = models.FloatField()
    unit = models.CharField(max_length=255, blank=True, null=True)
    unit_price = models.FloatField()
    details_idx = models.IntegerField(blank=True, null=True)
    unit_drug_avg_cost = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prescription_detail'
        app_label = 'cmsinv'
