from django.db import models
from django.utils import timezone

# for using pymongo
# from db_connection import db

# Waitlist = db['Waitlist']
# Client = db['Client']
# Chat_Group = db['Chat_Group']
# Chat = db['Chat']
# Routes = db['Routes']
# MunicipalityPermit = db['MunicipalityPermit']
# MunicipalityData = db['MunicipalityData']
# Create your models here.

# class Source(models.Model):
#     text = models.CharField(max_length=255)
#     favicon = models.URLField()
#     title = models.CharField(max_length=100)

#     def __str__(self):
#         return self.text

# class FollowUp(models.Model):
#     question = models.CharField(max_length=255)
#     answer = models.TextField()

    # def __str__(self):
    #     return self.question

# class Message(models.Model):
#     user_chat = models.TextField()
#     bot_chat_answer = models.TextField()

#     def __str__(self):
#         return self.user_chat

# class Chat(models.Model):
#     message = models.ForeignKey(Message, related_name='chats', on_delete=models.CASCADE)
#     sources = models.JSONField()
#     bot_chat_answer = models.TextField()
#     follow_up = models.JSONField()

#     def __str__(self):
#         return self.message.user_chat

class Client_Municipality(models.Model):
    ACCOUNT_TYPE_CHOICES = (
        ('M', 'Member'),
        ('C', 'Customer'),
    )
    # username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    municipality = models.CharField(max_length=255)
    residential_permits_qty = models.CharField(max_length=255)
    commercial_permits_qty = models.CharField(max_length=255)
    approving_request = models.CharField(max_length=255) 
    agree = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    status = models.BooleanField(default=True)
    account_type = models.CharField(max_length=1, default='M')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # address = models.TextField()
    # organization = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def check_username(username):
        try:
            Client_Municipality.objects.get(username=username)
            return True
        except Client_Municipality.DoesNotExist:
            return False

    @staticmethod
    def check_email(email):
        try:
            Client_Municipality.objects.get(email=email)
            return True
        except Client_Municipality.DoesNotExist:
            return False
        
    @staticmethod
    def check_phone(phone):
        try:
            Client_Municipality.objects.get(phone=phone)
            return True
        except:
            return False
        

class Client_Commercial(models.Model):
    ACCOUNT_TYPE_CHOICES = (
        ('M', 'Member'),
        ('C', 'Customer'),
    )
    # username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    # address = models.TextField()
    phone = models.CharField(max_length=15)
    municipality = models.CharField(max_length=100)
    rpr = models.CharField(max_length=100)
    cpr = models.CharField(max_length=100)
    intrested = models.CharField(max_length=100)
    agree = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    # occupation = models.CharField(max_length=100, blank=True, null=True)
    account_type = models.CharField(max_length=1, default='C')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def check_username(username):
        try:
            Client_Commercial.objects.get(username=username)
            return True
        except Client_Commercial.DoesNotExist:
            return False

    @staticmethod
    def check_email(email):
        try:
            Client_Commercial.objects.get(email=email)
            return True
        except Client_Commercial.DoesNotExist:
            return False
        
    @staticmethod
    def check_phone(phone):
        try:
            Client_Commercial.objects.get(phone=phone)
            return True
        except:
            return False
        

# from djongo.models.fields import ObjectIdField

class Chat_Group(models.Model):
    client_id = models.CharField(max_length=255)
    heading = models.TextField(max_length=255)  # Adjust the max_length as needed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.heading}"
    
# client_id = models.ForeignKey(Client, on_delete=models.CASCADE)

# client_id = models.ForeignKey(Client)
    # client_id = models.OneToOneField(
    #     Client,
    #     on_delete=models.CASCADE,
    #     null=True
    # )
class Chat(models.Model):
    # group_id = models.ForeignKey(Chat_Group)
    # group_id = models.OneToOneField(
    #     Chat_Group,
    #     on_delete=models.CASCADE,
    #     null=True
    # )
    # client = models.ForeignKey(Client)  # Add a foreign key relationship with the Client model
    # client = models.OneToOneField(
    #     Client,
    #     on_delete=models.CASCADE,
    #     null=True
    # )
    message = models.TextField()
    bot_chat_answer = models.TextField()
    follow_up = models.JSONField(null=True)  # Nullable field
    sources = models.JSONField(null=True)    # Nullable field

    def __str__(self):
        return f"{self}"
    


class Routes(models.Model):
    url = models.URLField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url
    


# dictonary base structure for municipality table

class MunicipalityPermit(models.Model):
    permit_number = models.CharField(max_length=100, unique=True)
    pdf_file = models.FileField(upload_to='municipality_pdfs/')

    def __str__(self):
        return self.permit_number

class MunicipalityData(models.Model):
    permit = models.OneToOneField(MunicipalityPermit, on_delete=models.CASCADE, related_name='municipality_data')
    zoning_parameters = models.JSONField(default=dict)
    analyze_plumbing = models.JSONField(default=dict)
    analyze_electrical = models.JSONField(default=dict)
    analyze_mechanical = models.JSONField(default=dict)
    analyze_arborist = models.JSONField(default=dict)
    analyze_residential_code = models.JSONField(default=dict)

    def __str__(self):
        return f"Municipality Data for Permit: {self.permit.permit_number}"
    

# structure data table of municiliplity
# class MunicipalityPermit(models.Model):
#     permit_number = models.CharField(max_length=100, unique=True)
#     pdf_file = models.FileField(upload_to='municipality_pdfs/')

# class ZoningParameter(models.Model):
#     permit = models.ForeignKey(MunicipalityPermit, related_name='zoning_parameters', on_delete=models.CASCADE)
#     zoning_class = models.CharField(max_length=100)
#     item_value = models.CharField(max_length=100)
#     code_requirement = models.CharField(max_length=100)
#     pass_fail = models.BooleanField(default=False)
#     image = models.ImageField(upload_to='municipality_images/', blank=True, null=True)

# class AnalyzePlumbing(models.Model):
#     permit = models.ForeignKey(MunicipalityPermit, related_name='analyze_plumbing', on_delete=models.CASCADE)
#     type_of_check = models.CharField(max_length=100)
#     item = models.CharField(max_length=100)
#     value = models.CharField(max_length=100)
#     code_requirement = models.CharField(max_length=100)
#     pass_fail = models.BooleanField(default=False)

# class AnalyzeElectrical(models.Model):
#     permit = models.ForeignKey(MunicipalityPermit, related_name='analyze_electrical', on_delete=models.CASCADE)
#     type_of_check = models.CharField(max_length=100)
#     item = models.CharField(max_length=100)
#     value = models.CharField(max_length=100)
#     code_requirement = models.CharField(max_length=100)
#     pass_fail = models.BooleanField(default=False)

# class AnalyzeMechanical(models.Model):
#     permit = models.ForeignKey(MunicipalityPermit, related_name='analyze_mechanical', on_delete=models.CASCADE)
#     type_of_check = models.CharField(max_length=100)
#     item = models.CharField(max_length=100)
#     value = models.CharField(max_length=100)
#     pass_fail = models.BooleanField(default=False)

# class AnalyzeArborist(models.Model):
#     permit = models.ForeignKey(MunicipalityPermit, related_name='analyze_arborist', on_delete=models.CASCADE)
#     type = models.CharField(max_length=100)
#     item = models.CharField(max_length=100)
#     value = models.CharField(max_length=100)

# class AnalyzeResidentialCode(models.Model):
#     permit = models.ForeignKey(MunicipalityPermit, related_name='analyze_residential_code', on_delete=models.CASCADE)
#     type_of_check = models.CharField(max_length=100)
#     item = models.CharField(max_length=100)
#     value = models.CharField(max_length=100)
#     code_requirement = models.CharField(max_length=100)
#     pass_fail = models.BooleanField(default=False)


class VerifyEmail(models.Model):
    email = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email}"
    
class VerifyForgetEmail(models.Model):
    email = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email}"
