import json
from pyairtable import Api
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from .models import WaitlistUser, MContactInfo
from django.db import transaction, IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class WaitlistUserView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            occupation = data.get('occupation')
            comments = data.get('comments')
            
            with transaction.atomic():
                waitlist_user_data = WaitlistUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                occupation=occupation,
                comments=comments
                )
                api = Api(settings.AIRTABLE_ACCESS_TOKEN)
                table = api.table(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_DEVELOPERS_TABLE_ID)
                table.create({
                    "Full Name": f'{first_name} {last_name}',
                    "Email": email,
                    "Occupation": occupation,
                    "Comments": comments
                    })
            return JsonResponse(
                    {'message': 'User added to waitlist successfully!', 'data': {'id': waitlist_user_data.id}},
                    status=201
                )
        
        except IntegrityError as e:
            return JsonResponse({'error': 'Email already exists.'}, status=400)
        
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, 
                status=400
            )
        
@method_decorator(csrf_exempt, name='dispatch')
class MContactInfoView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            phone = data.get('phone')
            municipality = data.get('municipality')
            residential_permits_qty = data.get('residential_permits_qty')
            commercial_permits_qty = data.get('commercial_permits_qty')
            approving_requests = data.get('approving_requests')

            with transaction.atomic():
                mcontact_info_data = MContactInfo.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    municipality=municipality,
                    residential_permits_qty=residential_permits_qty,
                    commercial_permits_qty=commercial_permits_qty,
                    approving_requests=approving_requests
                )
                api = Api(settings.AIRTABLE_ACCESS_TOKEN)
                table = api.table(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_MUNICIPALITY_TABLE_ID)
                table.create({
                    "First Name": first_name, 
                    "Last Name": last_name, 
                    "Email": email, 
                    "Phone number": phone, 
                    "Municipality": municipality, 
                    "No. of Residential Permits": residential_permits_qty, 
                    "No. of Commercial Permits": commercial_permits_qty, 
                    "Approving Permits": "yes" if approving_requests == True else "no"
                    })
            return JsonResponse(
                    {'message': 'Contact information saved successfully!', 'data': {'id': mcontact_info_data.id}},
                    status=201
                )
        
        except IntegrityError as e:
            return JsonResponse({'error': 'Email or phone number already exists.'}, status=400)
        
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, 
                status=400
            )