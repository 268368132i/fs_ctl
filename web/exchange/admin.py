from django.contrib import admin
from .models import ConfFlags
from .models import Conference
from .models import ConfUser
from .models import Assignment
from .models import FixedEndpoint,ParamsCache,Settings,Asset,Recording


# Register your models here.

admin.site.register(Conference)
admin.site.register(ConfUser)
admin.site.register(Assignment)
admin.site.register(ConfFlags)
admin.site.register(FixedEndpoint)
admin.site.register(ParamsCache)
admin.site.register(Settings)
admin.site.register(Asset)
admin.site.register(Recording)
