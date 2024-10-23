from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .helpers import municipality_LLM
from main_application.models import MunicipalityPermit, MunicipalityData

@csrf_exempt
def get_municipality_response(request):
    if request.method == "POST":
        # Assuming 'file' is the key for the PDF file in the POST request
        pdf_file = request.FILES.get('file')
        user_message = request.POST.get('user_message', '')

        if pdf_file is None:
            return JsonResponse({'error': 'No PDF file provided'}, status=400)
        
        # Call municipality_LLM to save data and get permit_number
        permit_number = municipality_LLM(user_message, pdf_file)

        response_data = {
            'permit_number': permit_number,
            'pdf_file_name': pdf_file.name,
            'user_message': user_message,
        }
        return JsonResponse(response_data)

    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
def permit_info(request, permit_number):
    try:
        permit = MunicipalityPermit.objects.get(permit_number=permit_number)
        municipality_data = MunicipalityData.objects.get(permit=permit)

        data = {
            'permit_number': permit.permit_number,
            'pdf_file': permit.pdf_file.url,
            'zoning_parameters': municipality_data.zoning_parameters,
            'analyze_plumbing': municipality_data.analyze_plumbing,
            'analyze_electrical': municipality_data.analyze_electrical,
            'analyze_mechanical': municipality_data.analyze_mechanical,
            'analyze_arborist': municipality_data.analyze_arborist,
            'analyze_residential_code': municipality_data.analyze_residential_code,
        }

        return JsonResponse(data, status=200)
    except MunicipalityPermit.DoesNotExist:
        return JsonResponse({'error': 'Permit not found'}, status=404)
    except MunicipalityData.DoesNotExist:
        return JsonResponse({'error': 'Data not found for this permit'}, status=404)