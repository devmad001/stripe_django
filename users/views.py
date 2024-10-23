import os
import json
import uuid
from datetime import datetime
from django.views import View
from django.http import JsonResponse
from IQbackend.helpers import processAddress
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from users.models import ProfileSettings, Report
from IQbackend.connectors import sendgrid_connector
from django.template.loader import render_to_string
from IQbackend.mixins.auth import LoginRequiredMixin
from IQbackend.connectors.s3_connector import S3Connector
from IQbackend.mixins.subscribed import SubscriptionRequiredMixin

class UploadProfilePictureView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            s3_connector = S3Connector()
            file = request.FILES.get("profile_pic")
            if not file:
                return JsonResponse({'error': 'Profile picture is required'}, status=400)
            file_name, file_extension = os.path.splitext(file.name)
            file_path = f"profile_pictures/{request.user.id}/{uuid.uuid4()}{file_extension}"
            s3_connector.upload_file(file_path, file)

            settings = ProfileSettings.objects.get(
                user=request.user
            )
            settings.profile_picture = file_path
            settings.save()

            return JsonResponse({"message": "Profile picture uploaded successfully"})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class GetProfilePictureView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            settings = ProfileSettings.objects.get(
                user=request.user
            )
            profile_picture_path = settings.profile_picture

            if not profile_picture_path:
                return JsonResponse({"error": "No profile picture found"}, status=404)

            s3_connector = S3Connector()
            presigned_url = s3_connector.generate_presigned_get_url(
                file_path=profile_picture_path,
                expires_in_seconds=240,
                metadata=None
            )

            return JsonResponse({"presigned_url": presigned_url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ProfileSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            settings = model_to_dict(ProfileSettings.objects.get(
                user=request.user
            ))

            return JsonResponse(
                {'data' : settings}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
    
    def patch(self, request):
        try:
            data = json.loads(request.body)
            settings = ProfileSettings.objects.get(
                user=request.user
            )
            
            for key, value in data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)

            settings.save()

            return JsonResponse(
                {
                    'message': 'Profile settings updated successfully.',
                    'data' : model_to_dict(settings)
                }, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )

class UpdateReportCostView(LoginRequiredMixin, View):
    def patch(self, request, report_id):
        try:
            report = get_object_or_404(Report, id=report_id, user=request.user)

            data = json.loads(request.body)
            acquisition_cost = data.get('acquisition_cost')
            other_cost = data.get('other_cost')

            if acquisition_cost is not None:
                report.acquisition_cost = acquisition_cost
            if other_cost is not None:
                report.other_cost = other_cost

            report.save()

            return JsonResponse({
                'message': 'Report updated successfully!'
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ReportsView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            address = data.get('address')
            address = processAddress(request, address)

            report, created = Report.objects.get_or_create(
                user=request.user, 
                address=address['full_address']
            )

            if created:
                return JsonResponse(
                    {
                        'message': 'Report created successfully!', 
                        'data': {'id': report.id}
                    }, 
                    status=201
                )
            else:
                return JsonResponse(
                    {'message': 'Report is already created.',
                     'data': {'id': report.id},
                    }, 
                    status=200
                )
            
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
        
    def get(self, request):
        try:
            reports = list(Report.objects.filter(
                user=request.user
            ).values())

            return JsonResponse(
                {'data' : reports}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )


class GetReportView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def get(self, request, report_id):
        try:
            report = get_object_or_404(
                Report, 
                id=report_id, 
                user=request.user
            )

            report_data = {
                'id': report.id,
                'address': report.address,
                'property': report.property,
                'kpis': report.kpis,
                'comparable_sales': report.comparable_sales,
                'zoning': report.zoning,
                'selected_plan': report.selected_plan.id,
                'architectural_plans': list(report.architectural_plans.values())
            }

            return JsonResponse(
                {'data' : report_data}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )


class SendReportEmailView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request, report_id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email', None)
            report = Report.objects.get(
                id=report_id, 
                user=request.user
            )

            if email == None:
                email = request.user.username

            sendgrid = sendgrid_connector.SendgridConnector()

            html_content = render_to_string(
                'report.html', 
                {'report': report,
                 'date': datetime.now().strftime('%B %d, %Y')}
            )
            response = sendgrid.send_report(
                email,
                report.address,
                html_content
            )

            return JsonResponse(
                {'message': 'Report sent via email.'}, 
                status=200
            )

        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
        