import json
import uuid
from main_application.models import MunicipalityPermit, MunicipalityData

def municipality_LLM(user_message, pdf_file):
    # Generate a unique permit number using UUID
    permit_number = str(uuid.uuid4())

    # Create a MunicipalityPermit
    permit = MunicipalityPermit.objects.create(permit_number=permit_number, pdf_file=pdf_file)
    # Create a MunicipalityPermit
    # permit = MunicipalityPermit.objects.create(permit_number="123456", pdf_file=pdf_file)

    # Create the data for MunicipalityData
    municipality_data = {
        "zoning_parameters": [
            {
                "zoninig_class": "R4",
                "item_value": "Single Family Dwelling",
                "code_requirement": "Pass",
                "pass_fail": True,
                "image": "path/to/zoning_image.jpg"
            },
            {
                "zoninig_class": "R4",
                "item_value": "18116",
                "code_requirement": "9000",
                "pass_fail": False,
            },
            # Add more zoning parameters data as needed
        ],
        "analyze_plumbing": [
            {
                "type_of_check": "Water Supply System",
                "item": "Compliance with minimum pipe diameter",
                "value": "3 inches",
                "code_requirement": "2 inches",
                "pass_fail": True
            },
            {
                "type_of_check": "Water Supply System",
                "item": "Backflow prevention: [Required]",
                "value": "Yes",
                "code_requirement": "Provided",
                "pass_fail": False
            },
            # Add more analyze plumbing data as needed
        ],
        "analyze_electrical": [
            {
                "type_of_check": "Electrical Service and Distribution",
                "item": "Compliance with service size and capacity requirements",
                "value": "Compliant",
                "code_requirement": "Compliant",
                "pass_fail": True
            },
            {
                "type_of_check": "Branch Circuits, Feeders, and Conductors",
                "item": "Compliance with requirements for branch circuits",
                "value": "Compliant",
                "code_requirement": "Compliant",
                "pass_fail": True
            },
            # Add more analyze electrical data as needed
        ],
        "analyze_mechanical": [
            {
                "type_of_check": "System Design and Equipment",
                "item": "Compliance with IBC for system design",
                "value": "Compliant",
                "pass_fail": True
            },
            {
                "type_of_check": "Ductwork Design",
                "item": "Adequacy of duct sizing",
                "value": "Adequate",
                "pass_fail": True
            },
            # Add more analyze mechanical data as needed
        ],
        "analyze_arborist": [
            {
                "type": "Tree",
                "item": "Trees within 50 feet",
                "value": "No"
            },
            {
                "type": "Tree",
                "item": "Age of Tree survey less than two years",
                "value": "Yes"
            },
            # Add more analyze arborist data as needed
        ],
        "analyze_residential_code": [
            {
                "type_of_check": "Foundation Design",
                "item": "Compliance with IBC requirements for soil bearing capacity",
                "value": "Compliant",
                "code_requirement": "Compliant",
                "pass_fail": True
            },
            {
                "type_of_check": "Structural Frame and Load Bearing Walls",
                "item": "Compliance with design loads",
                "value": "Compliant",
                "code_requirement": "Compliant",
                "pass_fail": True
            },
            # Add more analyze residential code data as needed
        ]
    }

    # Convert the dictionary data to JSON
    json_data = json.dumps(municipality_data)

    # Create a MunicipalityData instance and associate it with the permit
    municipality_data_instance = MunicipalityData.objects.create(
        permit=permit,
        zoning_parameters=municipality_data['zoning_parameters'],
        analyze_plumbing=municipality_data['analyze_plumbing'],
        analyze_electrical=municipality_data['analyze_electrical'],
        analyze_mechanical=municipality_data['analyze_mechanical'],
        analyze_arborist=municipality_data['analyze_arborist'],
        analyze_residential_code=municipality_data['analyze_residential_code']
    )

    # Save the updated data
    municipality_data_instance.save()

    # Return the permit_number
    return permit.permit_number