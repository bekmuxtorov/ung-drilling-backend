"""
Django Management Command: populate_drilling_bpa

Vazifasi:
1. Bazada kerakli barcha katalog / ma'lumotnoma obyektlarini (Enterprise, Area, Region,
   Employee, Position, MachineType, DepthsLayers, Resources, Unit) yaratish (yoki mavjudini olish).
2. DrillingBPA jadvaliga 5 ta (yoki ko'rsatilgan miqdorda) to'laqonli operatsiya obyektini qo'shish.
3. Har bir yaratilgan DrillingBPA obyektiga unga tegishli bo'lgan barcha 5 ta modelning
   (WellDesign, WellDesignInLength, DepthsLayersLength, DailyWorkDescriptionBPA, AvailableResourcesBPA)
   har biriga 5 tadan realistik qiymat yaratib biriktirish.
4. Tranzaksion xavfsizlik (atomic transaction), chiroyli konsol statistikasi va
   takroriy chaqirishlar uchun professional moslashuvchanlik.
"""

from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.directory.models import (
    Area,
    DepthsLayers,
    Employee,
    Enterprise,
    MachineType,
    Position,
    Region,
    Resources,
    Unit,
)
from apps.operations.models import (
    AvailableResourcesBPA,
    DailyWorkDescriptionBPA,
    DepthsLayersLength,
    DrillingBPA,
    WellDesign,
    WellDesignInLength,
    WellDesignPeriodType,
    WellDesignType,
)


class Command(BaseCommand):
    help = (
        "DrillingBPA ga 5 ta obyekt va unga tegishli har bir modelga (WellDesign, "
        "WellDesignInLength, DepthsLayersLength, DailyWorkDescriptionBPA, AvailableResourcesBPA) "
        "5 tadan qiymat qo'shish buyrug'i."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Yaratilishi kerak bo'lgan DrillingBPA obyektlari soni (standart: 5 ta)."
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Yangi ma'lumot qo'shishdan oldin mavjud DrillingBPA obyektlarini tozalash."
        )

    def handle(self, *args, **options):
        count: int = options["count"]
        clean: bool = options["clean"]

        self.stdout.write(self.style.MIGRATE_HEADING("=" * 70))
        self.stdout.write(self.style.MIGRATE_HEADING(" DRILLING BPA & BOG'LIQ MODELLARNI TO'LDIRISH BOSHLANDI "))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 70))

        try:
            with transaction.atomic():
                if clean:
                    self.stdout.write(self.style.WARNING("Eski DrillingBPA ma'lumotlari tozalanmoqda..."))
                    deleted_count, _ = DrillingBPA.objects.all().delete()
                    self.stdout.write(
                        self.style.SUCCESS(f"Mavjud {deleted_count} ta operatsiya va ularga bog'liq ma'lumotlar o'chirildi.")
                    )

                # 1-QADAM: Barcha zaruriy ma'lumotnomalarni (Directory) bazada yaratib olish
                self.stdout.write(self.style.HTTP_INFO("\n[1/3] Katalog va ma'lumotnomalar bazada tayyorlanmoqda..."))
                catalogs = self._prepare_directory_catalogs()
                self._print_catalog_summary(catalogs)

                # 2-QADAM: DrillingBPA obyektlarini yaratish
                self.stdout.write(self.style.HTTP_INFO(f"\n[2/3] {count} ta DrillingBPA obyekti yaratilmoqda..."))
                created_bpas = self._create_drilling_bpas(count=count, catalogs=catalogs)

                # 3-QADAM: Har bir DrillingBPA uchun har bir bog'liq modelga 5 tadan qiymat biriktirish
                self.stdout.write(
                    self.style.HTTP_INFO(
                        "\n[3/3] Har bir DrillingBPA ga 5 ta bog'liq model bo'yicha 5 tadan qiymat biriktirilmoqda..."
                    )
                )
                stats = self._attach_related_model_data(created_bpas=created_bpas, catalogs=catalogs)

                self._print_final_report(created_bpas=created_bpas, stats=stats)

        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"\nXatolik yuz berdi va barcha amallar bekor qilindi (rollback): {exc}"))
            raise exc

    def _prepare_directory_catalogs(self) -> Dict[str, list]:
        """
        Bazada kerakli barcha ma'lumotnomalarni professional tarzda get_or_create
        orqali mavjudligini ta'minlaydi va ro'yxat shaklida qaytaradi.
        """
        now = timezone.now()

        # 1. Hududlar (Region)
        regions_data = [
            "Qashqadaryo viloyati",
            "Buxoro viloyati",
            "Qoraqalpog'iston Respublikasi",
            "Surxondaryo viloyati",
            "Andijon viloyati",
        ]
        regions = []
        for name in regions_data:
            reg, _ = Region.objects.get_or_create(name=name)
            regions.append(reg)

        # 2. Maydonlar / Konlar (Area)
        areas_data = [
            ("Sho'rtan koni", regions[0]),
            ("Janubiy Kemachi koni", regions[0]),
            ("Gazli koni", regions[1]),
            ("Berdax koni", regions[2]),
            ("Xo'jaobod koni", regions[4]),
        ]
        areas = []
        for name, region in areas_data:
            area, _ = Area.objects.get_or_create(name=name, region=region)
            areas.append(area)

        # 3. Korxonalar (Enterprise)
        enterprises_data = [
            "Muborak neft va gaz qazib chiqarish boshqarmasi",
            "Sho'rtan neft va gaz qazib chiqarish boshqarmasi",
            "Gazli neft va gaz qazib chiqarish boshqarmasi",
            "Ustyurt qazib chiqarish boshqarmasi",
            "Andijon neft va gaz qazib chiqarish boshqarmasi",
        ]
        enterprises = []
        for name in enterprises_data:
            ent, _ = Enterprise.objects.get_or_create(name=name)
            enterprises.append(ent)

        # 4. Lavozimlar (Position)
        positions_data = [
            "Bosh burg'ulash muhandisi",
            "Katta burg'ulash texnologi",
            "Burg'ulash ustasi (Prorab)",
            "Burg'ulash eritmalari bo'yicha muhandis",
            "Geofizik nazoratchi muhandis",
        ]
        positions = []
        for name in positions_data:
            pos, _ = Position.objects.get_or_create(name=name)
            positions.append(pos)

        # 5. Xodimlar (Employee)
        employees_data = [
            ("Karimov Jasur Bahromovich", "+998901234561", positions[0]),
            ("Aliyev Bobur Mahmudovich", "+998912345672", positions[1]),
            ("Rahmonov Dilshod Rustamovich", "+998933456783", positions[2]),
            ("Salimov Olimjon Shuhratovich", "+998944567894", positions[3]),
            ("Yo'ldoshev Aziz Anvarovich", "+998955678905", positions[4]),
        ]
        employees = []
        for name, phone, pos in employees_data:
            emp, _ = Employee.objects.get_or_create(
                name=name,
                defaults={"phone_number": phone, "position": pos}
            )
            employees.append(emp)

        # 6. Burg'ulash dastgohlari va texnika turlari (MachineType)
        machines_data = [
            "Uralmash 3D-76 (Og'ir burg'ulash dastgohi)",
            "ZJ-70 DBS Burg'ulash majmuasi",
            "BU-5000/320 DGU statsionar dastgohi",
            "Honghua 50D Elektroyuritgichli qurilma",
            "Bentec HR-450 Avtomatlashtirilgan kompleksi",
        ]
        machine_types = []
        for name in machines_data:
            machine, _ = MachineType.objects.get_or_create(name=name)
            machine_types.append(machine)

        # 7. Chuqurlik qatlamlari (DepthsLayers) - kamida 5 ta xilma-xil qatlam
        layers_data = [
            "To'rtlamchi va Neogen yotqiziqlari (Alluvial qumtoshlar)",
            "Paleogen davri karbonat-gilli qatlamlari",
            "Yuqori Bo'r davri gil va alevrolitlari",
            "Quyi Bo'r davri qumtosh qatlamlari",
            "Yura davri mahsuldor karbonat jinslari",
        ]
        depth_layers = []
        for name in layers_data:
            layer, _ = DepthsLayers.objects.get_or_create(name=name)
            depth_layers.append(layer)

        # 8. O'lchov birliklari (Unit) - kamida 5 ta o'lchov birligi
        units_data = [
            "Tonna",
            "Litr",
            "Kilogramm",
            "Metr kub (m³)",
            "Dona",
        ]
        units = []
        for name in units_data:
            unit, _ = Unit.objects.get_or_create(name=name)
            units.append(unit)

        # 9. Moddiy resurslar (Resources) - kamida 5 ta neft-gaz resursi
        resources_data = [
            "Bentonit gil kukuni (Geltur)",
            "Barit og'irlashtirgich (KM-1)",
            "Dizel yoqilg'isi (DT-L-0.2)",
            "G-markali yuqori sifatli tamponaj sementi",
            "Polimer reagent (PAC-LV filtratsiyani kamaytiruvchi)",
        ]
        resources = []
        for name in resources_data:
            resource, _ = Resources.objects.get_or_create(name=name)
            resources.append(resource)

        return {
            "regions": regions,
            "areas": areas,
            "enterprises": enterprises,
            "positions": positions,
            "employees": employees,
            "machine_types": machine_types,
            "depth_layers": depth_layers,
            "units": units,
            "resources": resources,
        }

    def _print_catalog_summary(self, catalogs: Dict[str, list]) -> None:
        """Kataloglar bo'yicha tayyorlangan ma'lumotlar sonini ko'rsatish."""
        for key, val in catalogs.items():
            self.stdout.write(f"  ✓ {key.replace('_', ' ').capitalize()}: {len(val)} ta tayyor.")

    def _create_drilling_bpas(self, count: int, catalogs: Dict[str, list]) -> List[DrillingBPA]:
        """
        Bazada 5 ta (yoki count ta) DrillingBPA operatsiya obyektini yaratadi.
        """
        now = timezone.now()
        bpa_templates = [
            {
                "number": "BPA-2026/01-SH",
                "well_number": "101-G",
                "depth_plan": 3850,
                "days_offset": 30,
            },
            {
                "number": "BPA-2026/02-JK",
                "well_number": "45-JK",
                "depth_plan": 4200,
                "days_offset": 25,
            },
            {
                "number": "BPA-2026/03-GZ",
                "well_number": "78-Gazli",
                "depth_plan": 3500,
                "days_offset": 20,
            },
            {
                "number": "BPA-2026/04-BR",
                "well_number": "12-Berdax",
                "depth_plan": 4650,
                "days_offset": 15,
            },
            {
                "number": "BPA-2026/05-XJ",
                "well_number": "09-Xo'jaobod",
                "depth_plan": 3200,
                "days_offset": 10,
            },
        ]

        created_bpas: List[DrillingBPA] = []

        for idx in range(count):
            tpl = bpa_templates[idx % len(bpa_templates)]
            suffix = f"-{idx + 1}" if idx >= len(bpa_templates) else ""

            bpa = DrillingBPA.objects.create(
                number=f"{tpl['number']}{suffix}",
                enterprise=catalogs["enterprises"][idx % len(catalogs["enterprises"])],
                employee=catalogs["employees"][idx % len(catalogs["employees"])],
                area=catalogs["areas"][idx % len(catalogs["areas"])],
                well_number=f"{tpl['well_number']}{suffix}",
                machine_type=catalogs["machine_types"][idx % len(catalogs["machine_types"])],
                drilling_start_date=now - timedelta(days=tpl["days_offset"]),
                depth_plan=tpl["depth_plan"],
            )
            created_bpas.append(bpa)
            self.stdout.write(
                f"  + DrillingBPA #{bpa.id} yaratildi: {bpa.number} "
                f"({bpa.area.name}, Quduq №{bpa.well_number}, Reja: {bpa.depth_plan}m)"
            )

        return created_bpas

    def _attach_related_model_data(
        self,
        created_bpas: List[DrillingBPA],
        catalogs: Dict[str, list]
    ) -> Dict[str, int]:
        """
        Har bir DrillingBPA uchun 5 ta tegishli modelning har biriga 5 tadan qiymat qo'shadi:
        1. WellDesign (5 ta)
        2. WellDesignInLength (5 ta)
        3. DepthsLayersLength (5 ta)
        4. DailyWorkDescriptionBPA (5 ta)
        5. AvailableResourcesBPA (5 ta)
        """
        stats = {
            "well_designs": 0,
            "well_designs_in_length": 0,
            "depths_layers_lengths": 0,
            "daily_works": 0,
            "available_resources": 0,
        }

        now = timezone.now()

        for bpa_index, bpa in enumerate(created_bpas, start=1):
            start_date = bpa.drilling_start_date or (now - timedelta(days=20))

            # -------------------------------------------------------------
            # MODEL 1: WellDesign (Quduq konstruksiyasi - 5 ta qiymat)
            # -------------------------------------------------------------
            well_designs_data = [
                {
                    "type": WellDesignType.PLAN,
                    "pipe_diameter": 444.5,
                    "length": 150.0,
                    "start_date": start_date + timedelta(days=1),
                },
                {
                    "type": WellDesignType.PLAN,
                    "pipe_diameter": 324.0,
                    "length": 650.0,
                    "start_date": start_date + timedelta(days=4),
                },
                {
                    "type": WellDesignType.PLAN,
                    "pipe_diameter": 245.0,
                    "length": 1850.0,
                    "start_date": start_date + timedelta(days=10),
                },
                {
                    "type": WellDesignType.PLAN,
                    "pipe_diameter": 177.8,
                    "length": float(bpa.depth_plan - 350),
                    "start_date": start_date + timedelta(days=18),
                },
                {
                    "type": WellDesignType.FACT,
                    "pipe_diameter": 127.0,
                    "length": float(bpa.depth_plan),
                    "start_date": start_date + timedelta(days=25),
                },
            ]
            for item in well_designs_data:
                WellDesign.objects.create(
                    drilling_bpa=bpa,
                    type=item["type"],
                    pipe_diameter=item["pipe_diameter"],
                    length=item["length"],
                    start_date=item["start_date"],
                )
                stats["well_designs"] += 1

            # -------------------------------------------------------------
            # MODEL 2: WellDesignInLength (O'tish dinamikasi - 5 ta qiymat)
            # -------------------------------------------------------------
            designs_in_length_data = [
                {
                    "type": WellDesignPeriodType.DAY,
                    "length_plan": 35.0,
                    "length_fact": 38.0,
                    "start_date": start_date + timedelta(days=1),
                },
                {
                    "type": WellDesignPeriodType.DAY,
                    "length_plan": 40.0,
                    "length_fact": 42.5,
                    "start_date": start_date + timedelta(days=2),
                },
                {
                    "type": WellDesignPeriodType.DAY,
                    "length_plan": 45.0,
                    "length_fact": 44.0,
                    "start_date": start_date + timedelta(days=3),
                },
                {
                    "type": WellDesignPeriodType.DAY,
                    "length_plan": 48.0,
                    "length_fact": 51.0,
                    "start_date": start_date + timedelta(days=4),
                },
                {
                    "type": WellDesignPeriodType.DAY,
                    "length_plan": 52.0,
                    "length_fact": 55.5,
                    "start_date": start_date + timedelta(days=5),
                },
            ]
            for item in designs_in_length_data:
                WellDesignInLength.objects.create(
                    drilling_bpa=bpa,
                    type=item["type"],
                    length_plan=item["length_plan"],
                    length_fact=item["length_fact"],
                    start_date=item["start_date"],
                )
                stats["well_designs_in_length"] += 1

            # -------------------------------------------------------------
            # MODEL 3: DepthsLayersLength (Qatlam oraliqlari - 5 ta qiymat)
            # Bazada yaratilgan 5 ta DepthsLayers ga biriktiriladi
            # -------------------------------------------------------------
            layers_lengths = [250.0, 550.0, 1100.0, 950.0, 750.0]
            for idx, layer_obj in enumerate(catalogs["depth_layers"][:5]):
                DepthsLayersLength.objects.create(
                    drilling_bpa=bpa,
                    layer=layer_obj,
                    length=layers_lengths[idx],
                )
                stats["depths_layers_lengths"] += 1

            # -------------------------------------------------------------
            # MODEL 4: DailyWorkDescriptionBPA (Kunlik hisobot - 5 ta qiymat)
            # Har biri haqiqiy burg'ulash eritmasi parametrlari bilan
            # -------------------------------------------------------------
            daily_reports = [
                {
                    "days_ago": 5,
                    "desc": "Yo'naltiruvchi konduktor quduq stvoliga tushirildi va tamponaj eritmasi bilan sementlandi.",
                    "density": 1.18,
                    "viscosity": 36.0,
                    "fluid_loss": 6.5,
                    "mud_cake": 1.0,
                    "ph_level": 9.0,
                    "weight_on_bit": 12.0,
                    "rpm": 55.0,
                    "pump_pressure": 135.0,
                    "flow_rate": 26.0,
                },
                {
                    "days_ago": 4,
                    "desc": "Oraliq kolonna oralig'ida yangi doloto bilan burg'ulash davom ettirildi. Eritma aylanmasi me'yorda.",
                    "density": 1.20,
                    "viscosity": 38.0,
                    "fluid_loss": 6.2,
                    "mud_cake": 1.0,
                    "ph_level": 9.2,
                    "weight_on_bit": 14.5,
                    "rpm": 62.0,
                    "pump_pressure": 145.0,
                    "flow_rate": 28.5,
                },
                {
                    "days_ago": 3,
                    "desc": "Qatlam bosimi oshishi sababli eritma barit reagenti yordamida og'irlashtirildi va barqarorlandi.",
                    "density": 1.24,
                    "viscosity": 41.0,
                    "fluid_loss": 5.8,
                    "mud_cake": 1.1,
                    "ph_level": 9.4,
                    "weight_on_bit": 16.0,
                    "rpm": 68.0,
                    "pump_pressure": 158.0,
                    "flow_rate": 31.0,
                },
                {
                    "days_ago": 2,
                    "desc": "Mahsuldor gorizont oralig'ida stvolni kengaytirish va shlaklardan tozalash amaliyoti bajarildi.",
                    "density": 1.26,
                    "viscosity": 43.0,
                    "fluid_loss": 5.4,
                    "mud_cake": 1.2,
                    "ph_level": 9.6,
                    "weight_on_bit": 17.5,
                    "rpm": 74.0,
                    "pump_pressure": 165.0,
                    "flow_rate": 33.0,
                },
                {
                    "days_ago": 1,
                    "desc": "Doloto ko'tarildi, geofizik stansiya (GIS) orqali elektr va radioaktiv karotaj tadqiqotlari olib borildi.",
                    "density": 1.27,
                    "viscosity": 44.0,
                    "fluid_loss": 5.0,
                    "mud_cake": 1.2,
                    "ph_level": 9.7,
                    "weight_on_bit": 8.0,
                    "rpm": 45.0,
                    "pump_pressure": 120.0,
                    "flow_rate": 24.0,
                },
            ]
            for rep in daily_reports:
                DailyWorkDescriptionBPA.objects.create(
                    drilling_bpa=bpa,
                    report_date=(now - timedelta(days=rep["days_ago"])).date(),
                    description=rep["desc"],
                    density=rep["density"],
                    viscosity=rep["viscosity"],
                    fluid_loss=rep["fluid_loss"],
                    mud_cake=rep["mud_cake"],
                    ph_level=rep["ph_level"],
                    weight_on_bit=rep["weight_on_bit"],
                    rpm=rep["rpm"],
                    pump_pressure=rep["pump_pressure"],
                    flow_rate=rep["flow_rate"],
                )
                stats["daily_works"] += 1

            # -------------------------------------------------------------
            # MODEL 5: AvailableResourcesBPA (Mavjud resurslar - 5 ta qiymat)
            # Bazada yaratilgan 5 ta Resources va Unit lari bilan biriktiriladi
            # -------------------------------------------------------------
            resource_values = [
                (45.0, "Boshlang'ich burg'ulash eritmasi tayyorlash uchun ajratilgan bentonit zaxirasi"),
                (60.0, "Yuqori bosimli qatlamlarda eritma zichligini ko'tarish uchun og'irlashtirgich"),
                (18000.0, "Burg'ulash qurilmasi dizel generatorlari va yordamchi texnikalar uchun yoqilg'i"),
                (85.0, "Konduktor va foydalanish kolonnalari orqa qismini mustahkamlovchi tamponaj sementi"),
                (1500.0, "Burg'ulash eritmasi filtratsiyasini pasaytiruvchi yuqori molekulyar polimer reagent"),
            ]
            for idx in range(5):
                res_obj = catalogs["resources"][idx]
                unit_obj = catalogs["units"][idx]
                val, desc = resource_values[idx]

                AvailableResourcesBPA.objects.create(
                    drilling_bpa=bpa,
                    resources=res_obj,
                    unit=unit_obj,
                    value=val,
                    description=desc,
                )
                stats["available_resources"] += 1

            self.stdout.write(
                f"  ✓ BPA #{bpa.id} ({bpa.number}): 5 ta modelning har biriga 5 tadan (jami 25 ta) yozuv biriktirildi."
            )

        return stats

    def _print_final_report(
        self,
        created_bpas: List[DrillingBPA],
        stats: Dict[str, int]
    ) -> None:
        """Jarayon yakunida chiroyli yakuniy hisobot chiqarish."""
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS(" MUVAFFAQIYATLI YAKUNLANDI (NATIJALAR HISOBOTI)"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(f"• Yaratilgan DrillingBPA obyektlari soni: {len(created_bpas)} ta")
        self.stdout.write("• Har bir DrillingBPA ga biriktirilgan tegishli modellar:")
        self.stdout.write(f"   1. WellDesign (Quduq konstruksiyasi):                {stats['well_designs']} ta")
        self.stdout.write(f"   2. WellDesignInLength (O'tish dinamikasi):           {stats['well_designs_in_length']} ta")
        self.stdout.write(f"   3. DepthsLayersLength (Qatlam oraliqlari):           {stats['depths_layers_lengths']} ta")
        self.stdout.write(f"   4. DailyWorkDescriptionBPA (Kunlik hisobotlar):      {stats['daily_works']} ta")
        self.stdout.write(f"   5. AvailableResourcesBPA (Mavjud resurslar):         {stats['available_resources']} ta")
        total_sub_records = sum(stats.values())
        self.stdout.write(self.style.SUCCESS(f"• Jami biriktirilgan qo'shimcha yozuvlar: {total_sub_records} ta"))
        self.stdout.write(self.style.SUCCESS("=" * 70 + "\n"))
