from django.contrib.admin import SimpleListFilter
from django.db.models import Count

class DuplicateItemCmsidFilter(SimpleListFilter):

    title = 'Duplicates'
    parameter_name = 'cmsid'

    def lookups(self, request, model_admin):
        return (
            ('duplicates', 'Duplicates'),
        )
        

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'duplicates':
            dupes = (
                queryset.values("cmsid")
                .annotate(cms_id_count=Count("cmsid"))
                .filter(cms_id_count__gt=1)
            )
            print(dupes)
            return queryset.filter(
                cmsid__in=[i["cmsid"] for i in dupes]
            ).order_by("cmsid")