from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.common.models import AuditLog, AuditAction
from apps.common.context import set_current_audit_context, reset_current_audit_context
from apps.directory.models import MachineType, Unit, Region, Enterprise, Area
from apps.operations.models import DrillingBPA

User = get_user_model()


class AuditLogSignalAndModelTests(TestCase):
    """
    AuditLog modeli, signallar orqali avtomatik qayd qilish,
    eski va yangi qiymatlarni (Diff) to'g'ri aniqlash testlari.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="auditor_user",
            password="password123",
            first_name="Alisher",
            last_name="Qodirov"
        )

    def test_model_create_triggers_audit_log(self):
        """Model yaratilganda AuditLog ga CREATE yozuvi tushishini tekshirish."""
        # Initial count
        init_count = AuditLog.objects.filter(model_name="MachineType").count()

        # Create model
        m = MachineType.objects.create(name="Maxsus Ekskavator CAT-320")

        # Check log
        log = AuditLog.objects.filter(model_name="MachineType", object_id=str(m.pk)).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, AuditAction.CREATE)
        self.assertEqual(log.model_name, "MachineType")
        self.assertEqual(log.app_label, "directory")
        self.assertEqual(log.new_values["name"], "Maxsus Ekskavator CAT-320")
        self.assertEqual(log.old_values, {})
        self.assertIn("name", log.changes)
        self.assertIsNone(log.changes["name"]["old"])
        self.assertEqual(log.changes["name"]["new"], "Maxsus Ekskavator CAT-320")

    def test_model_update_triggers_audit_log_with_diff(self):
        """Model tahrirlanganda eski va yangi qiymatlar (diff) qayd etilishi."""
        u = Unit.objects.create(name="Litr (test)")
        AuditLog.objects.filter(model_name="Unit", object_id=str(u.pk)).delete()

        # Update name
        u.name = "Kub metr (m3) (yangilandi)"
        u.save()

        log = AuditLog.objects.filter(model_name="Unit", object_id=str(u.pk)).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, AuditAction.UPDATE)
        self.assertIn("name", log.changes)
        self.assertEqual(log.changes["name"]["old"], "Litr (test)")
        self.assertEqual(log.changes["name"]["new"], "Kub metr (m3) (yangilandi)")
        self.assertEqual(log.old_values["name"], "Litr (test)")
        self.assertEqual(log.new_values["name"], "Kub metr (m3) (yangilandi)")

    def test_model_update_no_changes_does_not_duplicate_log(self):
        """Maydonlar o'zgarmasdan save() chaqirilsa, ortiqcha log yozilmasligi."""
        u = Unit.objects.create(name="Dona (dona)")
        initial_log_count = AuditLog.objects.filter(model_name="Unit", object_id=str(u.pk)).count()

        # Hech narsa o'zgarmasdan qayta saqlash
        u.save()
        new_log_count = AuditLog.objects.filter(model_name="Unit", object_id=str(u.pk)).count()
        self.assertEqual(initial_log_count, new_log_count)

    def test_model_delete_triggers_audit_log(self):
        """Model o'chirilganda DELETE yozuvi eski qiymatlar bilan saqlanishi."""
        m = MachineType.objects.create(name="Vaqtinchalik Uskuna")
        m_pk = str(m.pk)
        m.delete()

        del_log = AuditLog.objects.filter(model_name="MachineType", object_id=m_pk, action=AuditAction.DELETE).first()
        self.assertIsNotNone(del_log)
        self.assertEqual(del_log.action, AuditAction.DELETE)
        self.assertEqual(del_log.old_values["name"], "Vaqtinchalik Uskuna")
        self.assertEqual(del_log.new_values, {})
        self.assertIn("name", del_log.changes)
        self.assertEqual(del_log.changes["name"]["old"], "Vaqtinchalik Uskuna")
        self.assertIsNone(del_log.changes["name"]["new"])


class AuditLogAPITests(TestCase):
    """
    AuditLog REST API endpointlari (/api/v1/audit-logs/),
    IP, MAC ID, User Agent aniqlanishi va Read-Only xavfsizlik testlari.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="admin_operator",
            password="securepassword123",
            first_name="Jasur",
            last_name="Bekov",
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)

    def test_request_captures_user_ip_and_mac_id(self):
        """
        API orqali o'zgarish qilinganda so'rovdagi User, IP va MAC ID
        AuditLog da to'g'ri qayd etilishini tekshirish.
        """
        custom_mac = "00:1A:2B:3C:4D:5E"
        custom_ip = "192.168.1.155"

        # Directory API orqali yangi mashina turi yaratamiz
        payload = {"name": "G'ildirakli kran 50t"}
        response = self.client.post(
            '/api/v1/machine-types/',
            payload,
            format='json',
            HTTP_X_FORWARDED_FOR=custom_ip,
            HTTP_X_MAC_ADDRESS=custom_mac,
            HTTP_USER_AGENT="UNG-Inspection-Client/1.0"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = str(response.data['id'])

        # AuditLog tekshiramiz
        log = AuditLog.objects.filter(model_name="MachineType", object_id=created_id).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.username, "admin_operator")
        self.assertEqual(log.user_full_name, "Jasur Bekov")
        self.assertEqual(log.ip_address, custom_ip)
        self.assertEqual(log.mac_address, custom_mac)
        self.assertEqual(log.user_agent, "UNG-Inspection-Client/1.0")
        self.assertEqual(log.action, AuditAction.CREATE)

    def test_audit_logs_list_api(self):
        """GET /api/v1/audit-logs/ ro'yxat olish, qidiruv va filtrlash."""
        # 1 ta log yaratamiz
        MachineType.objects.create(name="Audit Test Uskuna")

        response = self.client.get('/api/v1/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(len(results) >= 1)

        item = results[0]
        self.assertIn('action', item)
        self.assertIn('action_display', item)
        self.assertIn('ip_address', item)
        self.assertIn('mac_address', item)
        self.assertIn('changes', item)
        self.assertIn('old_values', item)
        self.assertIn('new_values', item)

    def test_audit_logs_filter_by_action_and_model(self):
        """Action va model_name bo'yicha filtrlash."""
        MachineType.objects.create(name="Model 1")

        res_filtered = self.client.get('/api/v1/audit-logs/?model_name=MachineType&action=create')
        self.assertEqual(res_filtered.status_code, status.HTTP_200_OK)
        results = res_filtered.data.get('results', res_filtered.data)
        for r in results:
            self.assertEqual(r['model_name'], 'MachineType')
            self.assertEqual(r['action'], 'create')

    def test_audit_logs_retrieve_api(self):
        """GET /api/v1/audit-logs/{id}/ bitta logni olish."""
        log = AuditLog.objects.create(
            username="test_admin",
            ip_address="10.0.0.5",
            mac_address="AA:BB:CC:DD:EE:FF",
            action=AuditAction.UPDATE,
            app_label="directory",
            model_name="Unit",
            object_id="999",
            object_repr="Unit #999",
            changes={"name": {"old": "Dona", "new": "Metr"}},
            old_values={"name": "Dona"},
            new_values={"name": "Metr"}
        )

        response = self.client.get(f'/api/v1/audit-logs/{log.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], log.id)
        self.assertEqual(response.data['ip_address'], "10.0.0.5")
        self.assertEqual(response.data['mac_address'], "AA:BB:CC:DD:EE:FF")
        self.assertEqual(response.data['changes']['name']['old'], "Dona")
        self.assertEqual(response.data['changes']['name']['new'], "Metr")

    def test_audit_logs_read_only_security(self):
        """
        Audit loglari xavfsizligi: POST, PUT, DELETE so'rovlari
        405 Method Not Allowed qaytarishi shart (Append-Only tamoyili).
        """
        # POST
        res_post = self.client.post('/api/v1/audit-logs/', {"action": "create"})
        self.assertEqual(res_post.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # PUT
        res_put = self.client.put('/api/v1/audit-logs/1/', {"action": "update"})
        self.assertEqual(res_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # DELETE
        res_del = self.client.delete('/api/v1/audit-logs/1/')
        self.assertEqual(res_del.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
