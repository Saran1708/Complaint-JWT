from django.db import models

class Department(models.Model):
    deptName = models.CharField(max_length=50)

    def __str__(self):
        return self.deptName


class User(models.Model):
    fullName = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)   # raw password, exam style
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, related_name="users")

    def __str__(self):
        return self.fullName


class Complaint(models.Model):
    complaintId = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    complaintType = models.CharField(max_length=50)
    createdOn = models.DateField(auto_now_add=True)
    urgent = models.BooleanField(default=False)
    note = models.TextField()
    status = models.CharField(max_length=20, default="pending")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints")

    def __str__(self):
        return self.complaintId
