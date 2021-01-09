from django.contrib.admin import SimpleListFilter
from django.db.models import Count

class DuplicateRegNoFilter(SimpleListFilter):

    title = 'Duplicates'
    parameter_name = 'reg_no'

    def lookups(self, request, model_admin):
        return (
            ('duplicates', 'Duplicates'),
        )
        

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'duplicates':
            dupes = (
                queryset.values("reg_no")
                .annotate(reg_no_count=Count("reg_no"))
                .filter(reg_no_count__gt=1)
            )
            print(dupes)
            return queryset.filter(
                reg_no__in=[i["reg_no"] for i in dupes]
            ).order_by("reg_no")