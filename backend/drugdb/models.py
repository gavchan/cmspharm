from django.db import models

class RegisteredDrug(models.Model):
    """
    Stores list of products/drugs
    """
    # Product Name
    name = models.CharField(max_length=255, blank=True, null=True)
    # Permit No.
    permit_no = models.CharField(unique=True, max_length=255, blank=True, null=True)
    # Active ingredients
    ingredients = models.TextField(blank=True, null=True)
    # Company Name and Company Address
    company = models.ForeignKey(
        'Company', on_delete=models.CASCADE,
        )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=['permit_no']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('drugdb.views.details', args=[str(self.permit_no)])
  
    def __str__(self):
        return '{} | {} ({})'.format(
            self.permit_no, self.name, self.ingredients
        )

class Company(models.Model):
    """
    Stores list of company names and addresses
    """
    # Company Name
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    # Company Address
    address = models.TextField(blank=True, null=True)
    # Companies imported from official source are certificate holders
    is_certholder = models.BooleanField(default=True)
    # Companies may also be a supplier
    is_supplier = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Companies'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('drugdb.views.details', args=[str(self.id)])
    
    def __str__(self):
        return '{} @ {}'.format(
            self.name, self.address
        )
