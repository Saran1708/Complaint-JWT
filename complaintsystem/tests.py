from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import User, Department, Complaint

class ComplaintAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create Departments
        self.dept_citizen = Department.objects.create(deptName="citizen")
        self.dept_admin = Department.objects.create(deptName="admin")

        # Create Users
        self.citizen = User.objects.create(
            fullName="Arjun Reddy",
            email="arjun@gmail.com",
            password="1234",
            dept=self.dept_citizen
        )
        self.admin = User.objects.create(
            fullName="Admin User",
            email="admin@gmail.com",
            password="admin123",
            dept=self.dept_admin
        )

        # Create Complaint for testing
        self.complaint = Complaint.objects.create(
            complaintId="CMP001",
            description="Garbage not collected",
            complaintType="sanitation",
            urgent=True,
            note="very urgent",
            status="pending",
            user=self.citizen
        )

    def get_token(self, email, password):
        response = self.client.post("/login/", {
            "email": email,
            "password": password
        })
        return response.data.get("token")

    def test_login_success(self):
        token = self.get_token("arjun@gmail.com", "1234")
        self.assertIsNotNone(token)

    def test_complaint_list(self):
        token = self.get_token("arjun@gmail.com", "1234")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/complaints/?status=pending")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_add_complaint_citizen(self):
        token = self.get_token("arjun@gmail.com", "1234")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post("/complaints/add/", {
            "complaintId": "CMP002",
            "description": "Street light issue",
            "complaintType": "electrical",
            "urgent": False,
            "note": "needs fixing",
            "status": "pending",
        })

        self.assertEqual(response.status_code, 201)

    def test_add_complaint_admin_not_allowed(self):
        token = self.get_token("admin@gmail.com", "admin123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post("/complaints/add/", {
            "complaintId": "CMP003",
            "description": "Issue",
            "complaintType": "general",
            "urgent": False,
            "note": "test note",
        })

        self.assertEqual(response.status_code, 403)

    def test_update_complaint_admin(self):
        token = self.get_token("admin@gmail.com", "admin123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.patch(f"/complaints/update/{self.complaint.id}/", {
            "status": "resolved"
        })

        self.assertEqual(response.status_code, 201)

    def test_delete_complaint_owner(self):
        token = self.get_token("arjun@gmail.com", "1234")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.delete(f"/complaints/delete/{self.complaint.id}/")
        self.assertEqual(response.status_code, 204)
