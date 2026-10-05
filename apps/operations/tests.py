from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.directory.models import (
    Enterprise,
    Employee,
    Position,
    Region,
    Area,
    MachineType,
    DepthsLayers,
    Resources,
    Unit,
)
from apps.operations.models import (
    DrillingBPA,
    WellDesign,
    WellDesignInLength,
    DepthsLayersLength,
    DailyWorkDescriptionBPA,
    AvailableResourcesBPA,
    WellDesignType,
    WellDesignPeriodType,
)

User = get_user_model()


class DrillingBPAModelAndPropertyTests(TestCase):
    """
    DrillingBPA va unga bog'liq barcha 6 ta modelning metodlari,
    hisoblanuvchi property'lari (current_depth, delta, delta_percent)
    va ma'lumotlar yaxlitligi bo'yicha testlar to'plami.
    """

    def setUp(self):
        # Ma'lumotnomalar
        self.region = Region.objects.create(name="Qashqadaryo")
        self.enterprise = Enterprise.objects.create(name="Sho'rtan NGBCh")
        self.position = Position.objects.create(name="Yetakchi muhandis")
        self.employee = Employee.objects.create(
            name="Rustamov Jasur",
            phone_number="+998901112233",
            position=self.position
        )
        self.area = Area.objects.create(name="Sho'rtan", region=self.region)
        self.machine_type = MachineType.objects.create(name="Uralmash 3D-76")
        self.layer_jurassic = DepthsLayers.objects.create(name="Yura davri")
        self.layer_cretaceous = DepthsLayers.objects.create(name="Bo'r davri")
        self.resource_diesel = Resources.objects.create(name="Yoqilg'i (Dizel)")
        self.unit_ton = Unit.objects.create(name="Tonna")

        # Asosiy BPA
        self.bpa = DrillingBPA.objects.create(
            number="BPA-2026/01",
            enterprise=self.enterprise,
            employee=self.employee,
            area=self.area,
            well_number="45",
            machine_type=self.machine_type,
            drilling_start_date=timezone.now(),
            depth_plan=3800
        )

    def test_bpa_str_representation(self):
        """BPA __str__ metodi to'g'ri matn qaytarishini tekshirish."""
        expected_str = f"BPA №BPA-2026/01 (Sho'rtan, Quduq №45)"
        self.assertEqual(str(self.bpa), expected_str)

    def test_current_depth_initial_zero(self):
        """Hisobotlar kiritilmaganda current_depth 0.0 bo'lishi kerak."""
        self.assertEqual(self.bpa.current_depth, 0.0)
        self.assertEqual(self.bpa.current_dept, 0.0)

    def test_current_depth_from_daily_well_design_in_length(self):
        """
        Kunlik (type='day') o'tish hisobotlari kiritilganda,
        current_depth ularning yig'indisini aniq hisoblab berishi kerak.
        """
        # 1-kun: 45.5 metr
        WellDesignInLength.objects.create(
            drilling_bpa=self.bpa,
            type=WellDesignPeriodType.DAY,
            length_plan=40.0,
            length_fact=45.5,
            start_date=timezone.now() - timedelta(days=2)
        )
        # 2-kun: 52.0 metr
        WellDesignInLength.objects.create(
            drilling_bpa=self.bpa,
            type=WellDesignPeriodType.DAY,
            length_plan=50.0,
            length_fact=52.0,
            start_date=timezone.now() - timedelta(days=1)
        )
        # Oylik yozuv (bu kunlik hisobga qo'shilmasligi kerak, agar kunlik mavjud bo'lsa)
        WellDesignInLength.objects.create(
            drilling_bpa=self.bpa,
            type=WellDesignPeriodType.MONTH,
            length_plan=1000.0,
            length_fact=1000.0,
            start_date=timezone.now()
        )

        self.assertEqual(self.bpa.current_depth, 97.5)
        self.assertEqual(self.bpa.current_dept, 97.5)

    def test_well_design_in_length_delta_and_percent_positive(self):
        """Fakt rejadan katta bo'lganda delta va delta_percent musbat bo'lishi."""
        item = WellDesignInLength.objects.create(
            drilling_bpa=self.bpa,
            type=WellDesignPeriodType.DAY,
            length_plan=50.0,
            length_fact=65.0
        )
        self.assertEqual(item.delta, 15.0)
        self.assertEqual(item.delta_percent, 30.0)

    def test_well_design_in_length_delta_and_percent_negative(self):
        """Fakt rejadan kam bo'lganda delta va delta_percent manfiy bo'lishi."""
        item = WellDesignInLength.objects.create(
            drilling_bpa=self.bpa,
            type=WellDesignPeriodType.DAY,
            length_plan=100.0,
            length_fact=80.0
        )
        self.assertEqual(item.delta, -20.0)
        self.assertEqual(item.delta_percent, -20.0)

    def test_well_design_in_length_zero_plan_division_by_zero_prevention(self):
        """length_plan=0 bo'lganda nolga bo'lish xatosi yuz bermasligi (0.0 qaytarishi)."""
        item = WellDesignInLength.objects.create(
            drilling_bpa=self.bpa,
            type=WellDesignPeriodType.DAY,
            length_plan=0.0,
            length_fact=25.0
        )
        self.assertEqual(item.delta, 25.0)
        self.assertEqual(item.delta_percent, 0.0)

    def test_well_design_creation_and_str(self):
        """WellDesign modelini yaratish va uning matn ifodasi."""
        wd = WellDesign.objects.create(
            drilling_bpa=self.bpa,
            type=WellDesignType.PLAN,
            pipe_diameter=324.0,
            length=800.0
        )
        self.assertIn("324.0mm", str(wd))
        self.assertIn("800.0m", str(wd))

    def test_depths_layers_length_str(self):
        """DepthsLayersLength modelini yaratish va uning matn ifodasi."""
        layer_length = DepthsLayersLength.objects.create(
            drilling_bpa=self.bpa,
            layer=self.layer_jurassic,
            length=1200.0
        )
        self.assertIn("Yura davri", str(layer_length))
        self.assertIn("1200.0m", str(layer_length))

    def test_daily_work_description_bpa_str(self):
        """DailyWorkDescriptionBPA modelini yaratish va uning matn ifodasi."""
        today = date.today()
        daily = DailyWorkDescriptionBPA.objects.create(
            drilling_bpa=self.bpa,
            report_date=today,
            description="Burg'ulash me'yorda ketmoqda",
            density=1.24,
            viscosity=48.0,
            pump_pressure=175.0
        )
        self.assertIn(str(today), str(daily))

    def test_available_resources_bpa_str(self):
        """AvailableResourcesBPA modelini yaratish va uning matn ifodasi."""
        ar = AvailableResourcesBPA.objects.create(
            drilling_bpa=self.bpa,
            resources=self.resource_diesel,
            unit=self.unit_ton,
            value=25.0,
            description="Ombordagi dizel yoqilg'isi"
        )
        self.assertIn("Yoqilg'i (Dizel): 25.0 Tonna", str(ar))


class BPAAPICRUDTests(TestCase):
    """
    Barcha 6 ta yangi BPA endpointlari bo'yicha to'liq REST API (CRUD),
    filtrlash, qidiruv va serializer testlari.
    """

    def setUp(self):
        self.client = APIClient()

        # Autentifikatsiya uchun foydalanuvchi
        self.user = User.objects.create_user(
            username="testdriller",
            password="testpassword123",
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        # Ma'lumotnomalar
        self.region = Region.objects.create(name="Buxoro")
        self.enterprise = Enterprise.objects.create(name="Muborak NGBCh")
        self.position = Position.objects.create(name="Prorab")
        self.employee = Employee.objects.create(name="Sobirov Aziz", position=self.position)
        self.area = Area.objects.create(name="Zevarda", region=self.region)
        self.machine_type = MachineType.objects.create(name="ZJ-50DBS")
        self.layer = DepthsLayers.objects.create(name="Bo'r qatlami")
        self.resource = Resources.objects.create(name="Sement G-100")
        self.unit = Unit.objects.create(name="Qop")

        # Test BPA
        self.bpa = DrillingBPA.objects.create(
            number="BPA-TEST-99",
            enterprise=self.enterprise,
            employee=self.employee,
            area=self.area,
            well_number="105",
            machine_type=self.machine_type,
            depth_plan=4000
        )

    def test_drilling_bpa_list_api(self):
        """GET /api/v1/drilling-bpas/ endpointini tekshirish."""
        response = self.client.get('/api/v1/drilling-bpas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Paginatsiya natijasi
        results = response.data.get('results', response.data)
        self.assertTrue(len(results) >= 1)
        item = results[0]
        self.assertEqual(item['well_number'], '105')
        self.assertIn('current_depth', item)
        self.assertIn('current_dept', item)
        self.assertEqual(item['enterprise']['name'], self.enterprise.name)

    def test_drilling_bpa_create_api(self):
        """POST /api/v1/drilling-bpas/ yangi BPA yaratish."""
        payload = {
            "number": "BPA-NEW-2026",
            "enterprise": self.enterprise.id,
            "employee": self.employee.id,
            "area": self.area.id,
            "well_number": "777",
            "machine_type": self.machine_type.id,
            "depth_plan": 3200
        }
        response = self.client.post('/api/v1/drilling-bpas/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['well_number'], "777")
        self.assertEqual(response.data['depth_plan'], 3200)

    def test_drilling_bpa_retrieve_detail_api(self):
        """GET /api/v1/drilling-bpas/{id}/ batafsil ma'lumotlarni tekshirish."""
        # Bog'liq ma'lumotlar qo'shamiz
        WellDesign.objects.create(
            drilling_bpa=self.bpa,
            type=WellDesignType.PLAN,
            pipe_diameter=245.0,
            length=1500.0
        )
        DailyWorkDescriptionBPA.objects.create(
            drilling_bpa=self.bpa,
            report_date=date.today(),
            description="Boshlang'ich quduq burg'ulash ishlari",
            density=1.18
        )

        response = self.client.get(f'/api/v1/drilling-bpas/{self.bpa.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Detail serializer ichma-ich bo'limlarni qaytarishi kerak
        self.assertIn('well_designs', response.data)
        self.assertIn('daily_works', response.data)
        self.assertIn('well_designs_in_length', response.data)
        self.assertIn('depths_layers_lengths', response.data)
        self.assertIn('available_resources', response.data)
        self.assertEqual(len(response.data['well_designs']), 1)
        self.assertEqual(len(response.data['daily_works']), 1)

    def test_drilling_bpa_patch_api(self):
        """PATCH /api/v1/drilling-bpas/{id}/ qisman yangilash."""
        payload = {"depth_plan": 4500}
        response = self.client.patch(f'/api/v1/drilling-bpas/{self.bpa.id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['depth_plan'], 4500)
        self.bpa.refresh_from_db()
        self.assertEqual(self.bpa.depth_plan, 4500)

    def test_drilling_bpa_filter_by_well_number(self):
        """Quduq raqami bo'yicha filtrlash."""
        response = self.client.get('/api/v1/drilling-bpas/?well_number=105')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

        response_empty = self.client.get('/api/v1/drilling-bpas/?well_number=99999')
        results_empty = response_empty.data.get('results', response_empty.data)
        self.assertEqual(len(results_empty), 0)

    def test_well_design_crud_api(self):
        """WellDesign API Create, List and Filter."""
        payload = {
            "drilling_bpa": self.bpa.id,
            "type": "plan",
            "pipe_diameter": 178.0,
            "length": 2500.0
        }
        res_post = self.client.post('/api/v1/well-designs/', payload, format='json')
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_post.data['pipe_diameter'], 178.0)

        # List with filter
        res_list = self.client.get(f'/api/v1/well-designs/?drilling_bpa={self.bpa.id}')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        results = res_list.data.get('results', res_list.data)
        self.assertEqual(len(results), 1)

    def test_well_design_in_length_api_with_properties(self):
        """WellDesignInLength API da delta va delta_percent to'g'ri kelishini tekshirish."""
        payload = {
            "drilling_bpa": self.bpa.id,
            "type": "day",
            "length_plan": 100.0,
            "length_fact": 125.0
        }
        res_post = self.client.post('/api/v1/well-designs-in-length/', payload, format='json')
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_post.data['delta'], 25.0)
        self.assertEqual(res_post.data['delta_percent'], 25.0)

    def test_depths_layers_length_api(self):
        """DepthsLayersLength API."""
        payload = {
            "drilling_bpa": self.bpa.id,
            "layer": self.layer.id,
            "length": 650.0
        }
        res_post = self.client.post('/api/v1/depths-layers-lengths/', payload, format='json')
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_post.data['layer']['name'], self.layer.name)

    def test_daily_work_description_bpa_api(self):
        """DailyWorkDescriptionBPA API."""
        payload = {
            "drilling_bpa": self.bpa.id,
            "report_date": "2026-10-05",
            "description": "Burg'ulash eritmasi parametrlari nazorat qilindi",
            "density": 1.25,
            "viscosity": 42.0,
            "fluid_loss": 5.5,
            "mud_cake": 1.0,
            "ph_level": 9.0,
            "weight_on_bit": 16.0,
            "rpm": 70.0,
            "pump_pressure": 190.0,
            "flow_rate": 30.0
        }
        res_post = self.client.post('/api/v1/daily-works-bpa/', payload, format='json')
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_post.data['density'], 1.25)
        self.assertEqual(res_post.data['flow_rate'], 30.0)

    def test_available_resources_bpa_api(self):
        """AvailableResourcesBPA API."""
        payload = {
            "drilling_bpa": self.bpa.id,
            "resources": self.resource.id,
            "unit": self.unit.id,
            "value": 500.0,
            "description": "500 qop sement yetkazildi"
        }
        res_post = self.client.post('/api/v1/available-resources-bpa/', payload, format='json')
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_post.data['resources']['name'], self.resource.name)
        self.assertEqual(res_post.data['unit']['name'], self.unit.name)
        self.assertEqual(res_post.data['value'], 500.0)
