from django.contrib import admin
from .models import (
    DerrickErectionOperation,
    OperationStage,
    DailyWorkDescription,
    DailyTransportItem,
)


class OperationStageInline(admin.TabularInline):
    model = OperationStage
    extra = 1
    fields = (
        'stage_type',
        'plan_days',
        'fact_days',
        'plan_start_date',
        'plan_end_date',
        'fact_start_date',
        'fact_end_date',
        'description',
    )


class DailyTransportItemInline(admin.TabularInline):
    model = DailyTransportItem
    extra = 1
    autocomplete_fields = ('transport_type',)
    fields = ('transport_type', 'count', 'description')


@admin.register(DerrickErectionOperation)
class DerrickErectionOperationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'from_area_display',
        'to_area_display',
        'enterprise',
        'drilling_rig_type',
        'foreman',
        'completion_percentage_display',
        'expected_drilling_date',
        'created_at',
    )
    list_filter = (
        'enterprise',
        'drilling_rig_type',
        'from_area__region',
        'to_area__region',
        'created_at',
    )
    search_fields = (
        'from_well_number',
        'to_well_number',
        'from_area__name',
        'to_area__name',
        'foreman__name',
    )
    autocomplete_fields = (
        'enterprise',
        'drilling_rig_type',
        'from_area',
        'to_area',
        'foreman',
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OperationStageInline]
    list_per_page = 25

    @admin.display(description="Qayerdan (Maydon / Quduq)")
    def from_area_display(self, obj):
        return f"{obj.from_area.name} (№{obj.from_well_number})"

    @admin.display(description="Qayerga (Maydon / Quduq)")
    def to_area_display(self, obj):
        return f"{obj.to_area.name} (№{obj.to_well_number})"

    @admin.display(description="Bajarilish (%)")
    def completion_percentage_display(self, obj):
        return f"{obj.completion_percentage}%"


@admin.register(OperationStage)
class OperationStageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'operation',
        'stage_type',
        'plan_days',
        'fact_days',
        'plan_start_date',
        'fact_start_date',
    )
    list_filter = ('stage_type', 'plan_start_date', 'fact_start_date')
    search_fields = ('operation__from_well_number', 'operation__to_well_number', 'description')
    autocomplete_fields = ('operation',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(DailyWorkDescription)
class DailyWorkDescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'derrick_erection_operation', 'short_description', 'created_at')
    list_filter = ('created_at', 'derrick_erection_operation__enterprise')
    search_fields = (
        'description',
        'derrick_erection_operation__from_well_number',
        'derrick_erection_operation__to_well_number',
    )
    autocomplete_fields = ('derrick_erection_operation',)
    inlines = [DailyTransportItemInline]
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    @admin.display(description="Ish tavsifi")
    def short_description(self, obj):
        if len(obj.description) > 60:
            return obj.description[:60] + "..."
        return obj.description


@admin.register(DailyTransportItem)
class DailyTransportItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'daily_work_description', 'transport_type', 'count', 'created_at')
    list_filter = ('transport_type', 'created_at')
    search_fields = ('description', 'transport_type__name')
    autocomplete_fields = ('daily_work_description', 'transport_type')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
