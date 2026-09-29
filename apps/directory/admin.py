from django.contrib import admin
from .models import (
    Enterprise,
    DrillingRigType,
    Region,
    Area,
    Foreman,
    TransportType,
    Position,
    Employee,
)


@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-id',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DrillingRigType)
class DrillingRigTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-id',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'areas_count', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description="Maydonlar soni")
    def areas_count(self, obj):
        return obj.areas.count()


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'created_at')
    list_filter = ('region', 'created_at')
    search_fields = ('name', 'region__name')
    autocomplete_fields = ('region',)
    ordering = ('-id',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Foreman)
class ForemanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'created_at')
    search_fields = ('name', 'phone')
    ordering = ('-id',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TransportType)
class TransportTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-id',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'employees_count', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description="Xodimlar soni")
    def employees_count(self, obj):
        return obj.employees.count()


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number', 'position', 'created_at')
    list_filter = ('position', 'created_at')
    search_fields = ('name', 'phone_number', 'position__name')
    autocomplete_fields = ('position',)
    ordering = ('-id',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
