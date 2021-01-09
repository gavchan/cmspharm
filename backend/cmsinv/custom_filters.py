from django.contrib.admin import SimpleListFilter
from django.db.models import Count

class DuplicateRegNoFilter(SimpleListFilter):

    title = 'Duplicates'
    parameter_name = 'registration_no'

    def lookups(self, request, model_admin):
        return (
            ('duplicates', 'Duplicates'),
        )
        

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'duplicates':
            dupes = (
                queryset.values("registration_no")
                .annotate(registration_no_count=Count("registration_no"))
                .filter(registration_no_count__gt=1)
            )
            print(dupes)
            return queryset.filter(
                registration_no__in=[i["registration_no"] for i in dupes]
            ).order_by("registration_no")