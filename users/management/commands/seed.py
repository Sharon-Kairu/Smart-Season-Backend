from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with admin and sample agents'

    def handle(self, *args, **kwargs):

        # Create Admin
        if not User.objects.filter(email='admin@smartseason.com').exists():
            User.objects.create_user(
                email='admin@smartseason.com',
                password='Admin@1234',
                full_name='SmartSeason Admin',
                role='admin',
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS('Admin created'))
        else:
            self.stdout.write('Admin already exists — skipping')

        # Create Agents
        agents = [
            {
                'email': 'agent1@smartseason.com',
                'password': 'Agent@1234',
                'full_name': 'John Mwangi',
                'phone_number': '+254700000001',
                'role': 'agent',
            },
            {
                'email': 'agent2@smartseason.com',
                'password': 'Agent@1234',
                'full_name': 'Mary Wanjiku',
                'phone_number': '+254700000002',
                'role': 'agent',
            },
            {
                'email': 'agent3@smartseason.com',
                'password': 'Agent@1234',
                'full_name': 'Peter Kamau',
                'phone_number': '+254700000003',
                'role': 'agent',
            },
        ]

        for agent_data in agents:
            if not User.objects.filter(email=agent_data['email']).exists():
                User.objects.create_user(**agent_data, is_active=True)
                self.stdout.write(self.style.SUCCESS(f"Agent {agent_data['full_name']} created"))
            else:
                self.stdout.write(f"Agent {agent_data['email']} already exists — skipping")

        self.stdout.write(self.style.SUCCESS('Seeding complete'))