from django.contrib import admin
from .models import (
    DerrickErectionOperation,
    OperationStage,
    DailyWorkDescription,
    DailyTransportItem,
    DrillingBPA,
    WellDesign,
    WellDesignInLength,
    DepthsLayersLength,
    DailyWorkDescriptionBPA,
    AvailableResourcesBPA,
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


class WellDesignInline(admin.TabularInline):
    model = WellDesign
    extra = 1
    fields = ('type', 'pipe_diameter', 'length', 'start_date')


class WellDesignInLengthInline(admin.TabularInline):
    model = WellDesignInLength
    extra = 1
    readonly_fields = ('delta_display', 'delta_percent_display')
    fields = ('type', 'length_plan', 'length_fact', 'delta_display', 'delta_percent_display', 'start_date')

    @admin.display(description="Farq (Delta)")
    def delta_display(self, obj):
        return f"{obj.delta} m" if obj.id else "—"

    @admin.display(description="Farq (%)")
    def delta_percent_display(self, obj):
        return f"{obj.delta_percent}%" if obj.id else "—"


class DepthsLayersLengthInline(admin.TabularInline):
    model = DepthsLayersLength
    extra = 1
    autocomplete_fields = ('layer',)
    fields = ('layer', 'length')


class AvailableResourcesBPAInline(admin.TabularInline):
    model = AvailableResourcesBPA
    extra = 1
    autocomplete_fields = ('resources', 'unit')
    fields = ('resources', 'unit', 'value', 'description')


@admin.register(DrillingBPA)
class DrillingBPAAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'number',
        'well_number',
        'area',
        'enterprise',
        'employee',
        'machine_type',
        'depth_plan',
        'current_depth_display',
        'drilling_start_date',
        'created_at',
    )
    list_filter = (
        'enterprise',
        'area__region',
        'area',
        'machine_type',
        'drilling_start_date',
        'created_at',
    )
    search_fields = (
        'number',
        'well_number',
        'area__name',
        'enterprise__name',
        'employee__name',
    )
    autocomplete_fields = (
        'enterprise',
        'employee',
        'area',
        'machine_type',
    )
    readonly_fields = ('current_depth', 'created_at', 'updated_at')
    inlines = [
        WellDesignInline,
        WellDesignInLengthInline,
        DepthsLayersLengthInline,
        AvailableResourcesBPAInline,
    ]
    list_per_page = 25

    @admin.display(description="Hozirgi chuqurlik (m)")
    def current_depth_display(self, obj):
        return f"{obj.current_depth} m"


@admin.register(WellDesign)
class WellDesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'drilling_bpa', 'type', 'pipe_diameter', 'length', 'start_date', 'created_at')
    list_filter = ('type', 'start_date')
    search_fields = ('drilling_bpa__well_number', 'drilling_bpa__number')
    autocomplete_fields = ('drilling_bpa',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(WellDesignInLength)
class WellDesignInLengthAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'drilling_bpa',
        'type',
        'length_plan',
        'length_fact',
        'delta',
        'delta_percent_display',
        'start_date',
    )
    list_filter = ('type', 'start_date')
    search_fields = ('drilling_bpa__well_number', 'drilling_bpa__number')
    autocomplete_fields = ('drilling_bpa',)
    readonly_fields = ('delta', 'delta_percent', 'created_at', 'updated_at')
    list_per_page = 25

    @admin.display(description="Farq (%)")
    def delta_percent_display(self, obj):
        return f"{obj.delta_percent}%"


@admin.register(DepthsLayersLength)
class DepthsLayersLengthAdmin(admin.ModelAdmin):
    list_display = ('id', 'drilling_bpa', 'layer', 'length', 'created_at')
    list_filter = ('layer',)
    search_fields = ('drilling_bpa__well_number', 'layer__name')
    autocomplete_fields = ('drilling_bpa', 'layer')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(DailyWorkDescriptionBPA)
class DailyWorkDescriptionBPAAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'drilling_bpa',
        'report_date',
        'density',
        'viscosity',
        'flow_rate',
        'pump_pressure',
        'created_at',
    )
    list_filter = ('report_date', 'created_at')
    search_fields = ('drilling_bpa__well_number', 'description')
    autocomplete_fields = ('drilling_bpa',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


@admin.register(AvailableResourcesBPA)
class AvailableResourcesBPAAdmin(admin.ModelAdmin):
    list_display = ('id', 'drilling_bpa', 'resources', 'value', 'unit', 'created_at')
    list_filter = ('resources', 'unit')
    search_fields = ('drilling_bpa__well_number', 'resources__name', 'description')
    autocomplete_fields = ('drilling_bpa', 'resources', 'unit')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

