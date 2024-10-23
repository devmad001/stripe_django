# Generated by Django 5.0.6 on 2024-06-27 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('architectural_plans', '0003_alter_architecturalplan_buy_url_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExteriorWallType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('2x4', 'Standard 2x4 exterior wall construction'), ('2x6', 'Standard 2x6 exterior wall construction'), ('2x8', 'Standard 2x8 exterior wall construction'), ('ICF', 'Insulated Concrete Form wall construction'), ('Container', 'Shipping container construction'), ('6x6 post', '6x6 post construction for exterior walls'), ('Block / CMU (main floor)', 'Concrete masonry unit construction for the main floor'), ('Metal', 'Metal exterior wall construction'), ('Post Frame', 'Post frame construction'), ('Log', 'Log exterior wall construction'), ('Block-Both Level', 'Block construction for both levels, metal building with wood')], default=None, help_text='Types of exterior walls like 2x4, 2x6 etc', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, help_text='Type of foundation like slab, basement, wall etc', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GarageLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Front', 'Garage located at the front of the house'), ('Side', 'Garage located at the side of the house'), ('Rear', 'Garage located at the rear of the house'), ('Courtyard', 'Garage located in a courtyard')], default=None, help_text='Location of garage i.e. side, front or courtyard etc', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GarageType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Drive Under', 'Garage where the main vehicle access is located beneath the living area.'), ('Attached', 'Garage that is directly attached to the main structure of the house.'), ('Detached', 'Garage that is separate from the main structure of the house.'), ('RV Garage', 'Garage designed specifically to accommodate recreational vehicles (RVs).'), ('Carport', 'A roofed structure for parking vehicles, typically not fully enclosed.')], default=None, help_text='Type of garage like attached, detached or none etc', max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='architecturalplan',
            name='height',
            field=models.FloatField(default=0.0, help_text='Height required to build based on the plan'),
        ),
        migrations.AddField(
            model_name='architecturalplan',
            name='units',
            field=models.IntegerField(default=0, help_text='Units correspond to plan types like single family, stand alone etc'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='architectural_style',
            field=models.CharField(choices=[('COASTAL CONTEMPORARY', 'A style that blends modern and coastal elements, often featuring open floor plans and large windows.'), ('NORTHWEST', 'A style characterized by the use of natural materials, large windows, and an emphasis on indoor-outdoor living.'), ('COUNTRY', 'A style that embodies rural charm, featuring porches, gables, and a welcoming, homey feel.'), ('VICTORIAN', 'A style known for its ornate detailing, asymmetrical facades, and steeply pitched roofs.'), ('NEW ORLEANS', 'A style that draws on French and Spanish influences, featuring wrought-iron balconies and courtyards.'), ('NEW AMERICAN', 'A modern take on traditional American architecture, often with open floor plans and mixed materials.'), ('A-FRAME', 'A style with a distinctive triangular shape, typically featuring steeply angled sides that meet at the top.'), ('SHINGLE', 'A style characterized by the use of shingles on the exterior, often with complex shapes and asymmetrical designs.'), ('SOUTHERN', 'A style that embodies the charm of the American South, with large porches, columns, and symmetry.'), ('BEACH', 'A style designed for coastal living, often featuring large windows, open spaces, and outdoor living areas.'), ('TRADITIONAL', 'A style that includes classic, timeless elements, often with symmetrical facades and formal layouts.'), ('FLORIDA', 'A style suited to the Florida climate, often featuring stucco exteriors, tiled roofs, and indoor-outdoor living spaces.'), ('SOUTHWEST', 'A style influenced by Spanish and Native American architecture, featuring stucco walls and flat roofs.'), ('LOUISIANA', 'A style that reflects the architectural heritage of Louisiana, with features like porches and French doors.'), ('LOG', 'A rustic style that uses logs for construction, often associated with cabins and natural settings.'), ('TUDOR', 'A style inspired by medieval English architecture, with steeply pitched roofs, decorative half-timbering, and tall windows.'), ('FARMHOUSE', 'A style that reflects rural farmhouses, often with large porches, gabled roofs, and simple, functional design.'), ('MODERN', 'A style characterized by clean lines, minimalism, and the use of modern materials and technologies.'), ('FRENCH COUNTRY', 'A style inspired by the French countryside, with rustic yet elegant features, such as stone exteriors and steep roofs.'), ('HILL COUNTRY', 'A style suited to hilly terrain, often featuring natural materials, large windows, and outdoor living areas.'), ('LAKE HOUSE', 'A style designed for lakefront living, with large windows, open floor plans, and outdoor spaces.'), ('COTTAGE', 'A cozy, quaint style often with a storybook quality, featuring steep roofs, small porches, and charming details.'), ('ACADIAN', 'A style that reflects the French colonial architecture of Louisiana, with steep roofs and large porches.'), ('RANCH', 'A single-story style with a long, low profile, often featuring large windows and open floor plans.'), ('MID CENTURY MODERN', 'A style from the mid-20th century, characterized by simplicity, integration with nature, and the use of modern materials.'), ('SOUTHERN TRADITIONAL', 'A style that combines elements of Southern and traditional architecture, with large porches and symmetrical facades.'), ('RUSTIC', 'A style that emphasizes natural materials and rugged, handcrafted elements, often with a cozy, cabin-like feel.'), ('SCANDINAVIAN', 'A minimalist style that emphasizes simplicity, functionality, and the use of natural light and materials.'), ('BARNDOMINIUM', 'A style that combines a barn and a condominium, often with an open floor plan and rustic elements.'), ('CAPE COD', 'A style originating from New England, characterized by a simple, symmetrical design with a steep roof and central chimney.'), ('COASTAL', 'A style designed for coastal environments, often featuring large windows, open spaces, and outdoor living areas.'), ('GEORGIAN', 'A style based on classical architecture, with symmetrical facades, columns, and decorative elements.'), ('CRAFTSMAN', 'A style that emphasizes handcrafted details, natural materials, and a connection to the surrounding environment.'), ('CARRIAGE', 'A style inspired by historic carriage houses, often featuring open floor plans and rustic elements.'), ('COLONIAL', "A style based on the architecture of America's colonial period, with symmetrical facades and traditional detailing."), ('MODERN FARMHOUSE', 'A contemporary take on the farmhouse style, blending modern elements with rustic, rural charm.'), ('BUNGALOW', 'A style that features a low-pitched roof, wide eaves, and a cozy, compact design, often with a front porch.'), ('CONTEMPORARY', 'A style that reflects current architectural trends, often featuring clean lines, large windows, and open spaces.'), ('ADOBE', 'A style that uses adobe (sun-dried bricks) as a primary material, common in Southwestern architecture.'), ('PRAIRIE', 'A style developed by Frank Lloyd Wright, characterized by horizontal lines, flat or hipped roofs, and integration with the landscape.'), ('CABIN', 'A small, rustic house often made from logs, typically found in rural or wilderness areas.'), ('LOW COUNTRY', 'A style from the coastal regions of the Southeastern US, featuring raised foundations and large porches.'), ('VACATION', 'A style designed for holiday homes, often with features that accommodate relaxation and recreation.'), ('EUROPEAN', 'A style inspired by the architecture of Europe, featuring elements like stone exteriors, steep roofs, and arched openings.'), ('MEDITERRANEAN', 'A style influenced by the architecture of Mediterranean countries, with stucco walls, tiled roofs, and outdoor living areas.'), ('MOUNTAIN', 'A style suited for mountainous regions, often with rugged materials, large windows, and integration with the natural landscape.')], default=None, help_text='Architectural style for the building', max_length=100),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_basement',
            field=models.FloatField(default=0.0, help_text='Area of basement'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_first_floor',
            field=models.FloatField(default=0.0, help_text='Area of first floor'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_garage',
            field=models.FloatField(default=0.0, help_text='Area of garage'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_second_floor',
            field=models.FloatField(default=0.0, help_text='Area of second floor'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_third_floor',
            field=models.FloatField(default=0.0, help_text='Area of third floor'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_total',
            field=models.FloatField(default=0.0, help_text='Total area required to build on the plan'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='bathrooms_count',
            field=models.FloatField(default=0.0, help_text='Total bathrooms included in plan. This is calculated based on bathrooms_full_count and bathrooms_half_count.'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='bathrooms_full_count',
            field=models.FloatField(default=0.0, help_text='Each of the value is counted as 1 unit in bathrooms_count'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='bathrooms_half_count',
            field=models.FloatField(default=0.0, help_text='Each of the value is counted as 0.5 in bathrooms_count'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='bedrooms_count',
            field=models.FloatField(default=0.0, help_text='Total bedrooms included in plan'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='buy_url',
            field=models.URLField(help_text='Url to buy plan from the source website'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='cars_capacity',
            field=models.FloatField(default=0.0, help_text='Number of cars that can be parked in garage'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='depth',
            field=models.FloatField(default=0.0, help_text='Depth required to build based on the plan'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='image_link',
            field=models.URLField(help_text='Image of the plan'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='plan_number',
            field=models.CharField(help_text='Plan number to uniquely identify architectural plan on source website', max_length=20),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='stories',
            field=models.FloatField(default=0.0, help_text='Number of floors in the architectural plan'),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='title',
            field=models.CharField(help_text='Title of the plan', max_length=255),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='width',
            field=models.FloatField(default=0.0, help_text='Width required to build based on the plan'),
        ),
        migrations.AddField(
            model_name='architecturalplan',
            name='exterior_wall_type',
            field=models.ManyToManyField(to='architectural_plans.exteriorwalltype'),
        ),
        migrations.AddField(
            model_name='architecturalplan',
            name='foundation',
            field=models.ManyToManyField(to='architectural_plans.foundation'),
        ),
        migrations.AddField(
            model_name='architecturalplan',
            name='garage_location',
            field=models.ManyToManyField(to='architectural_plans.garagelocation'),
        ),
        migrations.AddField(
            model_name='architecturalplan',
            name='garage_type',
            field=models.ManyToManyField(to='architectural_plans.garagetype'),
        ),
    ]