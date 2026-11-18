from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create an Administrator
        self.admin_user = User.objects.create_user(
            username='admin_saira',
            email='admin@school.edu',
            password='Password123!',
            first_name='Saira',
            last_name='Admin',
            role=User.Role.ADMIN,
            employee_id='ADM-001',
            department='Administration'
        )

        # Create an Employee
        self.employee_user = User.objects.create_user(
            username='employee_juan',
            email='juan@school.edu',
            password='Password123!',
            first_name='Juan',
            last_name='Dela Cruz',
            role=User.Role.EMPLOYEE,
            employee_id='EMP-001',
            department='High School Faculty'
        )

    # --- 1. Registration Tests ---
    def test_registration_success(self):
        """Users can register with valid fields; passwords must be hashed."""
        response = self.client.post(reverse('register'), {
            'username': 'new_staff',
            'email': 'newstaff@school.edu',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': User.Role.EMPLOYEE,
            'department': 'Science Dept',
            'employee_id': 'EMP-002',
            'contact_number': '+639123456789',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        # Verify user created and password hashed
        user = User.objects.get(username='new_staff')
        self.assertNotEqual(user.password, 'StrongPassword123!')
        self.assertTrue(user.check_password('StrongPassword123!'))
        self.assertEqual(user.role, User.Role.EMPLOYEE)

    def test_registration_password_mismatch(self):
        """Registration fails if passwords do not match."""
        response = self.client.post(reverse('register'), {
            'username': 'mismatch_user',
            'email': 'mismatch@school.edu',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password123!',
            'password_confirm': 'DifferentPassword123!',
            'role': User.Role.EMPLOYEE,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatch_user').exists())
        self.assertFormError(response.context['form'], 'password_confirm', 'Passwords do not match. Please re-enter.')

    def test_registration_duplicate_username_and_email(self):
        """Registration enforces unique username and unique email."""
        response = self.client.post(reverse('register'), {
            'username': 'employee_juan',  # existing username
            'email': 'unique@school.edu',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'role': User.Role.EMPLOYEE,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', 'A user with this username already exists.')

        response_email = self.client.post(reverse('register'), {
            'username': 'unique_user',
            'email': 'juan@school.edu',  # existing email
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'role': User.Role.EMPLOYEE,
        })
        self.assertEqual(response_email.status_code, 200)
        self.assertFormError(response_email.context['form'], 'email', 'An account with this email address is already registered.')

    # --- 2. Login & Logout Tests ---
    def test_login_with_username_success(self):
        """Employee logging in with username is directed to employee dashboard."""
        response = self.client.post(reverse('login'), {
            'username': 'employee_juan',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('employee_dashboard'))

    def test_login_with_email_success(self):
        """Admin logging in with email is directed to admin dashboard."""
        response = self.client.post(reverse('login'), {
            'username': 'admin@school.edu',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_login_invalid_credentials(self):
        """Invalid credentials show error and reject login."""
        response = self.client.post(reverse('login'), {
            'username': 'employee_juan',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid')

    def test_logout(self):
        """Logging out terminates the session and redirects to login."""
        self.client.login(username='employee_juan', password='Password123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    # --- 3. Role-Based Dashboard & Protection Tests ---
    def test_dashboard_redirect_for_roles(self):
        """Admin is redirected to admin dashboard; Employee is redirected to employee dashboard."""
        self.client.login(username='admin_saira', password='Password123!')
        resp_admin = self.client.get(reverse('dashboard_redirect'))
        self.assertRedirects(resp_admin, reverse('admin_dashboard'))

        self.client.logout()

        self.client.login(username='employee_juan', password='Password123!')
        resp_emp = self.client.get(reverse('dashboard_redirect'))
        self.assertRedirects(resp_emp, reverse('employee_dashboard'))

    def test_employee_cannot_access_admin_dashboard(self):
        """An employee cannot open the admin dashboard by typing its URL."""
        self.client.login(username='employee_juan', password='Password123!')
        response = self.client.get(reverse('admin_dashboard'))
        # Must be redirected to employee dashboard with access denied
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('employee_dashboard'))

    def test_admin_cannot_access_employee_dashboard(self):
        """An admin cannot open the employee dashboard by typing its URL."""
        self.client.login(username='admin_saira', password='Password123!')
        response = self.client.get(reverse('employee_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_unauthenticated_user_redirected_to_login(self):
        """Logged-out users trying to view protected pages are redirected to login."""
        protected_urls = [
            reverse('admin_dashboard'),
            reverse('employee_dashboard'),
            reverse('profile'),
            reverse('edit_profile'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('login'), response.url)

    # --- 4. User Profile Tests ---
    def test_profile_view_and_edit(self):
        """User can view and edit their own profile."""
        self.client.login(username='employee_juan', password='Password123!')

        # View profile
        resp_view = self.client.get(reverse('profile'))
        self.assertEqual(resp_view.status_code, 200)
        self.assertContains(resp_view, 'Juan Dela Cruz')
        self.assertContains(resp_view, 'juan@school.edu')

        # Edit profile
        resp_edit = self.client.post(reverse('edit_profile'), {
            'first_name': 'Juan Carlos',
            'last_name': 'Dela Cruz',
            'email': 'juancarlos@school.edu',
            'contact_number': '+63 999 888 7777',
            'department': 'Senior High School',
            'employee_id': 'EMP-001',
        })
        self.assertEqual(resp_edit.status_code, 302)
        self.assertRedirects(resp_edit, reverse('profile'))

        # Verify database updated
        self.employee_user.refresh_from_db()
        self.assertEqual(self.employee_user.first_name, 'Juan Carlos')
        self.assertEqual(self.employee_user.email, 'juancarlos@school.edu')
        self.assertEqual(self.employee_user.contact_number, '+63 999 888 7777')
