import csv
from django.core.management.base import BaseCommand
from architectural_plans.models import ArchitecturalPlan, GarageLocation, GarageType, Foundation, ExteriorWallType

class Command(BaseCommand):
    help = 'Populate ArchitecturalPlan table from CSV file'

    def handle(self, *args, **options):
        file_path = './ml_models/data/architectural_plans/architectural_plans_preprocessed.csv'
        start_row = 685
        end_row = 785

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for index, row in enumerate(reader):
                if index < start_row:
                    continue
                if end_row is not None and index > end_row:
                    break

                plan = ArchitecturalPlan.objects.create(
                    plan_number=row['plan_number'],
                    title=row['title'],
                    image_link=row['image_link'],
                    architectural_style=row['architectural_style'],
                    area_total=float(row['area_total']),
                    bedrooms_count=float(row['bedrooms_count']),
                    bathrooms_count=float(row['bathrooms_count']),
                    bathrooms_full_count=float(row['bathrooms_full_count']),
                    bathrooms_half_count=float(row['bathrooms_half_count']),
                    stories=float(row['stories']),
                    area_first_floor=float(row['area_first_floor']),
                    area_second_floor=float(row['area_second_floor']),
                    area_third_floor=float(row['area_third_floor']),
                    area_basement=float(row['area_basement']),
                    area_garage=float(row['area_garage']),
                    cars_capacity=float(row['cars_capacity']),
                    width=float(row['width']),
                    depth=float(row['depth']),
                    height=float(row['height']),
                    buy_url=row['buy_url'],
                    units=float(row['units'])
                )

                garage_locations = row['garage_location'].split(', ')
                garage_types = row['garage_type'].split(', ')
                foundations = row['foundation'].split(', ')
                exterior_wall_types = row['exterior_wall_type'].split(', ')

                for location in garage_locations:
                    location_obj, _ = GarageLocation.objects.get_or_create(name=location.strip())
                    plan.garage_location.add(location_obj)

                for garage_type in garage_types:
                    type_obj, _ = GarageType.objects.get_or_create(name=garage_type.strip())
                    plan.garage_type.add(type_obj)

                for foundation in foundations:
                    foundation_obj, _ = Foundation.objects.get_or_create(name=foundation.strip())
                    plan.foundation.add(foundation_obj)

                for wall_type in exterior_wall_types:
                    wall_obj, _ = ExteriorWallType.objects.get_or_create(name=wall_type.strip())
                    plan.exterior_wall_type.add(wall_obj)

                self.stdout.write(self.style.SUCCESS(f'Successfully created ArchitecturalPlan: {plan}'))

        self.stdout.write(self.style.SUCCESS('Finished populating ArchitecturalPlan table'))
