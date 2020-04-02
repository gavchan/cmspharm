from django.db import models

class RegisteredDrug(models.Model):
    """
    Stores list of products/drugs
    """
    # Product Name
    name = models.CharField(max_length=255, blank=True, null=True)
    # Permit No.
    permit_no = models.CharField(max_length=255, blank=True, null=True)
    # Active ingredients
    ingredients = models.TextField(blank=True, null=True)
    # Company Name and Company Address
    company = models.ForeignKey(
        'Company', on_delete=models.CASCADE,
        )

    def __str__(self):
        return '{} | {} - {}'.format(
            self.permit_no, self.product_name, self.company
        )

class Company(models.Model):
    """
    Stores list of company names and addresses
    """
    # Company Name
    name = models.CharField(max_length=255, blank=True, null=True)
    # Company Address
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{} @ {}'.format(
            self.name, self.address
        )
