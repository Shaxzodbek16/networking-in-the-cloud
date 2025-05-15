from django.db.utils import IntegrityError

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class UserModelTests(TestCase):

    def test_user_str_returns_username_and_role(self):
        user = User.objects.create_user(
            username="testuser", password="testpass", role="admin"
        )
        self.assertEqual(str(user), "testuser (admin)")

    def test_default_role_is_staff(self):
        user = User.objects.create_user(username="random", password="pass")
        self.assertEqual(user.role, "staff")
        self.assertEqual(str(user), "random (staff)")

    def test_can_create_admin_role(self):
        user = User.objects.create_user(
            username="admintest", password="pass", role="admin"
        )
        self.assertEqual(user.role, "admin")

    def test_can_create_manager_role(self):
        user = User.objects.create_user(
            username="managertest", password="pass", role="manager"
        )
        self.assertEqual(user.role, "manager")

    def test_role_choices_only_accept_valid(self):
        user = User(username="badrole", role="ceo")
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_cannot_create_duplicate_username(self):
        User.objects.create_user(username="uniqueuser", password="pass")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(username="uniqueuser", password="otherpass")

    def test_password_is_hashed(self):
        user = User.objects.create_user(username="hashme", password="plainpass123")
        self.assertNotEqual(user.password, "plainpass123")
        self.assertTrue(user.check_password("plainpass123"))

    def test_get_role_display(self):
        user = User.objects.create_user(
            username="manageruser", password="pass", role="manager"
        )
        self.assertEqual(user.get_role_display(), "manager")

    def test_ordering_is_by_date_joined(self):
        user1 = User.objects.create_user(username="user1", password="pass")
        user2 = User.objects.create_user(username="user2", password="pass")
        users = list(User.objects.all())
        self.assertLessEqual(users[0].date_joined, users[1].date_joined)

    def test_superuser_role_is_staff_by_default(self):
        admin = User.objects.create_superuser(username="superadmin", password="pass")
        self.assertEqual(admin.role, "staff")

    def test_repr_and_display_for_various_roles(self):
        for role, _ in User.ROLE_CHOICES:
            user = User.objects.create_user(
                username=f"user_{role}", password="pass", role=role
            )
            self.assertIn(role, str(user))
            self.assertEqual(user.get_role_display(), role)

    def test_user_cannot_have_blank_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", password="pass")

    def test_user_email_field_optional(self):
        user = User.objects.create_user(username="noemail", password="pass")
        self.assertEqual(user.email, "")

    def test_user_is_active_by_default(self):
        user = User.objects.create_user(username="someuser", password="pass")
        self.assertTrue(user.is_active)

    def test_superuser_flags(self):
        superuser = User.objects.create_superuser(username="theboss", password="pass")
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_regular_user_flags(self):
        user = User.objects.create_user(username="pleb", password="pass")
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_update_user_role(self):
        user = User.objects.create_user(
            username="changer", password="pass", role="staff"
        )
        user.role = "manager"
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.role, "manager")

    def test_get_role_display_still_works_after_update(self):
        user = User.objects.create_user(
            username="changer2", password="pass", role="staff"
        )
        user.role = "admin"
        user.save()
        self.assertEqual(user.get_role_display(), "admin")

    def test_date_joined_auto_now(self):
        user = User.objects.create_user(username="timestamped", password="pass")
        from datetime import datetime, timedelta

        now = datetime.now(user.date_joined.tzinfo)
        self.assertLessEqual(abs(now - user.date_joined), timedelta(seconds=10))

    def test_user_unicode_str(self):
        user = User.objects.create_user(
            username="unicode测试", password="pass", role="staff"
        )
        self.assertIn("unicode测试", str(user))

    def test_bulk_create_users(self):
        users = [User(username=f"bulkuser{i}", role="staff") for i in range(5)]
        User.objects.bulk_create(users)
        self.assertEqual(
            User.objects.filter(username__startswith="bulkuser").count(), 5
        )

    def test_user_deletion(self):
        user = User.objects.create_user(username="delete_me", password="pass")
        pk = user.pk
        user.delete()
        self.assertFalse(User.objects.filter(pk=pk).exists())

    def test_user_cannot_set_invalid_role_directly(self):
        user = User.objects.create_user(
            username="trybadrole", password="pass", role="staff"
        )
        user.role = "sus"
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_user_unique_constraint(self):
        User.objects.create_user(username="uniqueguy", password="pass")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(username="uniqueguy", password="pass2")

    def test_user_required_fields(self):
        with self.assertRaises(TypeError):
            User.objects.create_user()

    def test_user_blank_password(self):
        user = User.objects.create_user(username="blankpw", password="")
        self.assertTrue(user.has_usable_password())

    def test_user_in_admin_queryset(self):
        User.objects.create_superuser(username="adminx", password="adminpass")
        admin_users = User.objects.filter(is_superuser=True)
        self.assertEqual(admin_users.count(), 1)

    def test_user_repr(self):
        user = User.objects.create_user(
            username="repruser", password="pass", role="manager"
        )
        self.assertEqual(str(user), "repruser (manager)")
