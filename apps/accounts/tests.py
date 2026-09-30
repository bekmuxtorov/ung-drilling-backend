from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient
from rest_framework import status
import jwt
from django.conf import settings

from apps.accounts.models import Role
from apps.directory.models import Employee, Position

User = get_user_model()


class AccountsJWTAndRoleTests(TestCase):
    """
    User, Role, Permission va JWT Autentifikatsiya to'liq test to'plami.
    """

    def setUp(self):
        self.client = APIClient()

        # Lavozim va Xodim yaratish
        self.position = Position.objects.create(name="Bosh burg'ulovchi")
        self.employee = Employee.objects.create(
            name="Qodirov Alisher Bobirovich",
            phone_number="+998 90 123-45-67",
            position=self.position
        )

        # Ruxsatnomalar
        self.perm_view = Permission.objects.filter(codename='view_employee').first()
        self.perm_add = Permission.objects.filter(codename='add_employee').first()
        if not self.perm_view or not self.perm_add:
            # Agar mavjud bo'lmasa, test uchun yaratish
            from django.contrib.contenttypes.models import ContentType
            ct = ContentType.objects.get_for_model(Employee)
            self.perm_view, _ = Permission.objects.get_or_create(
                codename='view_employee',
                content_type=ct,
                defaults={'name': 'Can view employee'}
            )
            self.perm_add, _ = Permission.objects.get_or_create(
                codename='add_employee',
                content_type=ct,
                defaults={'name': 'Can add employee'}
            )

        # Rol yaratish va ruxsat biriktirish
        self.role_manager = Role.objects.create(name="Menejer")
        self.role_manager.permissions.add(self.perm_view, self.perm_add)

        # Superuser
        self.superuser = User.objects.create_superuser(
            username="admin_super",
            email="admin@ung.uz",
            password="SuperPassword123!"
        )

        # Oddiy foydalanuvchi (Rol va Xodim bilan)
        self.user = User.objects.create_user(
            username="user_alisher",
            email="alisher@ung.uz",
            password="UserPassword123!",
            first_name="Alisher",
            last_name="Qodirov",
            role=self.role_manager,
            employee=self.employee
        )

    # ==========================================================================
    # 1. Modellar va RoleModelBackend (RBAC) Testlari
    # ==========================================================================

    def test_role_and_user_creation(self):
        """Rol va foydalanuvchi to'g'ri yaratilganligi va bog'langanligini tekshirish."""
        self.assertEqual(self.user.role.name, "Menejer")
        self.assertEqual(self.user.employee.name, "Qodirov Alisher Bobirovich")
        self.assertEqual(self.user.role_name, "Menejer")
        self.assertEqual(self.user.employee_name, "Qodirov Alisher Bobirovich")
        self.assertIn(self.perm_view, self.user.role.permissions.all())

    def test_role_model_backend_permissions(self):
        """
        RoleModelBackend orqali user.has_perm() rolga biriktirilgan
        ruxsatlarni to'g'ri tanishini tekshirish.
        """
        # Rol orqali berilgan ruxsat
        self.assertTrue(self.user.has_perm("directory.view_employee"))
        self.assertTrue(self.user.has_perm("directory.add_employee"))
        # Rolga berilmagan ruxsat
        self.assertFalse(self.user.has_perm("directory.delete_employee"))

        # get_all_permissions_list()
        all_perms = self.user.get_all_permissions_list()
        self.assertIn("directory.view_employee", all_perms)
        self.assertIn("directory.add_employee", all_perms)

    def test_superuser_has_all_permissions(self):
        """Superuser barcha ruxsatlarga ega ekanligini tekshirish."""
        self.assertTrue(self.superuser.has_perm("directory.delete_employee"))
        self.assertTrue(self.superuser.has_perm("any_app.any_permission"))

    # ==========================================================================
    # 2. JWT Autentifikatsiya (Login, Claims, Refresh, Verify) Testlari
    # ==========================================================================

    def test_jwt_login_success(self):
        """To'g'ri login va parol orqali JWT tokenlar va user obyektini olish."""
        response = self.client.post("/api/v1/auth/login/", {
            "username": "user_alisher",
            "password": "UserPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertIn("user", data)

        user_data = data["user"]
        self.assertEqual(user_data["username"], "user_alisher")
        self.assertEqual(user_data["role"]["name"], "Menejer")
        self.assertEqual(user_data["employee"]["name"], "Qodirov Alisher Bobirovich")
        self.assertIn("directory.view_employee", user_data["permissions"])

        # Token payload ichidagi custom claim'larni tekshirish
        payload = jwt.decode(data["access"], settings.SECRET_KEY, algorithms=["HS256"])
        self.assertEqual(payload["username"], "user_alisher")
        self.assertEqual(payload["role"], "Menejer")
        self.assertEqual(payload["employee_id"], self.employee.id)

    def test_jwt_login_invalid_credentials(self):
        """Noto'g'ri login yoki parol kiritilganda 401 qaytishi."""
        response = self.client.post("/api/v1/auth/login/", {
            "username": "user_alisher",
            "password": "WrongPassword!"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_login_inactive_user(self):
        """Bloklangan (is_active=False) foydalanuvchi tizimga kira olmasligi."""
        self.user.is_active = False
        self.user.save()

        response = self.client.post("/api/v1/auth/login/", {
            "username": "user_alisher",
            "password": "UserPassword123!"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_refresh(self):
        """Refresh token yordamida yangi access token olish."""
        login_res = self.client.post("/api/v1/auth/login/", {
            "username": "user_alisher",
            "password": "UserPassword123!"
        })
        refresh_token = login_res.json()["refresh"]

        refresh_res = self.client.post("/api/v1/auth/token/refresh/", {
            "refresh": refresh_token
        })
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_res.json())

    def test_jwt_token_verify(self):
        """Tokenning yaroqliligini tekshirish (Verify)."""
        login_res = self.client.post("/api/v1/auth/login/", {
            "username": "user_alisher",
            "password": "UserPassword123!"
        })
        access_token = login_res.json()["access"]

        verify_res = self.client.post("/api/v1/auth/token/verify/", {
            "token": access_token
        })
        self.assertEqual(verify_res.status_code, status.HTTP_200_OK)

        # Noto'g'ri token
        bad_res = self.client.post("/api/v1/auth/token/verify/", {
            "token": "invalid.jwt.token"
        })
        self.assertEqual(bad_res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==========================================================================
    # 3. Joriy Foydalanuvchi (/api/v1/auth/me/) va Parol Testlari
    # ==========================================================================

    def test_current_user_profile(self):
        """GET /api/v1/auth/me/ orqali shaxsiy profilni olish."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["username"], "user_alisher")
        self.assertEqual(data["role_detail"]["name"], "Menejer")
        self.assertEqual(data["employee_detail"]["name"], "Qodirov Alisher Bobirovich")
        self.assertIn("directory.view_employee", data["permissions"])

    def test_change_password(self):
        """Foydalanuvchi o'z parolini muvaffaqiyatli o'zgartirishi."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/v1/auth/change-password/", {
            "old_password": "UserPassword123!",
            "new_password": "BrandNewPassword2026!",
            "new_password_confirm": "BrandNewPassword2026!"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Yangi parol bilan tizimga kirish
        self.client.logout()
        login_res = self.client.post("/api/v1/auth/login/", {
            "username": "user_alisher",
            "password": "BrandNewPassword2026!"
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

    # ==========================================================================
    # 4. Rollar (Role) va Foydalanuvchilar (User) CRUD Testlari
    # ==========================================================================

    def test_role_crud(self):
        """Rollar yaratish, ruxsatlar biriktirish va o'chirish."""
        self.client.force_authenticate(user=self.superuser)

        # Rol yaratish
        create_res = self.client.post("/api/v1/auth/roles/", {
            "name": "Operator",
            "permissions": [self.perm_view.id]
        }, format="json")
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        role_id = create_res.json()["id"]

        # Rol ma'lumotlarini olish
        get_res = self.client.get(f"/api/v1/auth/roles/{role_id}/")
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_res.json()["permissions_detail"]), 1)

    def test_admin_set_user_password(self):
        """Admin tomonidan foydalanuvchi parolini qayta o'rnatish."""
        self.client.force_authenticate(user=self.superuser)
        res = self.client.post(f"/api/v1/auth/users/{self.user.id}/set-password/", {
            "new_password": "AdminResetPass999!",
            "new_password_confirm": "AdminResetPass999!"
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Yangi parol bilan kirish
        self.client.logout()
        login_res = self.client.post("/api/v1/auth/login/", {
            "username": "user_alisher",
            "password": "AdminResetPass999!"
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

    # ==========================================================================
    # 5. Global API Himoyasi (DEFAULT_PERMISSION_CLASSES) Testlari
    # ==========================================================================

    def test_unauthenticated_api_request_rejected(self):
        """Token bo'lmaganda himoyalangan API endpointga kirish bloklanishi (401)."""
        response = self.client.get("/api/v1/enterprises/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_api_request_allowed(self):
        """Yaroqli token bilan API endpointga kirish muvaffaqiyatli bo'lishi (200)."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/enterprises/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_endpoints_accessible(self):
        """Ochiq endpointlar (Swagger, OpenAPI schema) token talab qilmasligi."""
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
