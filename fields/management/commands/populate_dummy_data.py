from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from fields.models import Field, FieldHistory
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with dummy data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating dummy data...')

        # Create admin user if not exists
        admin, created = User.objects.get_or_create(
            email='admin@smartseason.com',
            defaults={
                'full_name': 'Admin User',
                'role': 'admin',
                'phone_number': '+254700000000',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin: {admin.email}'))
        else:
            self.stdout.write(f'Admin already exists: {admin.email}')

        # Create 3 agents
        agents_data = [
            {
                'email': 'john.mwangi@smartseason.com',
                'full_name': 'John Mwangi',
                'phone_number': '+254712345678',
            },
            {
                'email': 'mary.wanjiku@smartseason.com',
                'full_name': 'Mary Wanjiku',
                'phone_number': '+254798123456',
            },
            {
                'email': 'peter.kamau@smartseason.com',
                'full_name': 'Peter Kamau',
                'phone_number': '+254723456789',
            },
        ]

        agents = []
        for agent_data in agents_data:
            agent, created = User.objects.get_or_create(
                email=agent_data['email'],
                defaults={
                    'full_name': agent_data['full_name'],
                    'role': 'agent',
                    'phone_number': agent_data['phone_number'],
                }
            )
            if created:
                agent.set_password('agent123')
                agent.save()
                self.stdout.write(self.style.SUCCESS(f'Created agent: {agent.email}'))
            else:
                self.stdout.write(f'Agent already exists: {agent.email}')
            agents.append(agent)

        # Create 7 fields
        fields_data = [
            {
                'name': 'Field Alpha',
                'location': 'Kiambu County',
                'crop_type': 'Maize',
                'planting_date': date.today() - timedelta(days=45),
                'size_in_acres': 5.5,
                'stage': 'growing',
                'status': 'active',
            },
            {
                'name': 'Field Beta',
                'location': 'Nakuru County',
                'crop_type': 'Wheat',
                'planting_date': date.today() - timedelta(days=30),
                'size_in_acres': 8.0,
                'stage': 'growing',
                'status': 'active',
            },
            {
                'name': 'Field Gamma',
                'location': 'Nairobi County',
                'crop_type': 'Tomatoes',
                'planting_date': date.today() - timedelta(days=60),
                'size_in_acres': 3.2,
                'stage': 'ready',
                'status': 'active',
            },
            {
                'name': 'Field Delta',
                'location': 'Meru County',
                'crop_type': 'Coffee',
                'planting_date': date.today() - timedelta(days=90),
                'size_in_acres': 12.0,
                'stage': 'harvested',
                'status': 'completed',
            },
            {
                'name': 'Field Epsilon',
                'location': 'Kisumu County',
                'crop_type': 'Rice',
                'planting_date': date.today() - timedelta(days=20),
                'size_in_acres': 6.5,
                'stage': 'planted',
                'status': 'active',
            },
            {
                'name': 'Field Zeta',
                'location': 'Eldoret',
                'crop_type': 'Barley',
                'planting_date': date.today() - timedelta(days=55),
                'size_in_acres': 10.0,
                'stage': 'growing',
                'status': 'at_risk',
            },
            {
                'name': 'Field Eta',
                'location': 'Nyeri County',
                'crop_type': 'Tea',
                'planting_date': date.today() - timedelta(days=15),
                'size_in_acres': 4.8,
                'stage': 'planted',
                'status': 'active',
            },
        ]

        fields = []
        for i, field_data in enumerate(fields_data):
            # Assign agents to fields (some fields may be unassigned)
            assigned_agent = agents[i % len(agents)] if i < 6 else None
            
            field, created = Field.objects.get_or_create(
                name=field_data['name'],
                defaults={
                    **field_data,
                    'assigned_to': assigned_agent,
                    'created_by': admin,
                    'notes': f'Initial notes for {field_data["name"]}'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created field: {field.name}'))
                
                # Create some field history for demonstration
                if random.choice([True, False]):
                    FieldHistory.objects.create(
                        field=field,
                        changed_by=admin,
                        field_name='stage',
                        old_value='planted',
                        new_value=field.stage
                    )
                    self.stdout.write(f'  Added history for {field.name}')
                
                if field.stage in ['ready', 'harvested']:
                    FieldHistory.objects.create(
                        field=field,
                        changed_by=assigned_agent or admin,
                        field_name='stage',
                        old_value='growing',
                        new_value=field.stage
                    )
                    self.stdout.write(f'  Added additional history for {field.name}')
            else:
                self.stdout.write(f'Field already exists: {field.name}')
            fields.append(field)

        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Total Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Agents: {User.objects.filter(role="agent").count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Fields: {Field.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Field History: {FieldHistory.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\nDummy data created successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: admin@smartseason.com / admin123')
        self.stdout.write('  Agents: john.mwangi@smartseason.com / agent123')
        self.stdout.write('          mary.wanjiku@smartseason.com / agent123')
        self.stdout.write('          peter.kamau@smartseason.com / agent123')
