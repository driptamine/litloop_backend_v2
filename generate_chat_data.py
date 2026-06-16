import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev')
django.setup()

from users.models import User
from chats.models import Chat, Message
from django.utils import timezone

def generate_data_for_all_users():
    users = list(User.objects.all())
    user_count = len(users)
    
    if user_count < 2:
        print("Not enough users to generate chat data.")
        return

    print(f"Generating chat data for {user_count} users...")

    for user in users:
        # Each user will have at least 2 direct chats with other random users
        # We pick 2 other users to chat with
        others = [u for u in users if u.id != user.id]
        targets = random.sample(others, min(len(others), 2))

        for target in targets:
            # Create a direct chat
            chat_name = f"dm-{min(user.id, target.id)}-{max(user.id, target.id)}"
            chat, created = Chat.objects.get_or_create(
                name=chat_name,
                defaults={'description': f'Direct chat between {user.username} and {target.username}'}
            )
            
            if created:
                chat.participants.add(user, target)
                print(f"Created chat: {chat_name} ({user.username} & {target.username})")
                
                # Add initial messages only for newly created chats to avoid bloat
                Message.objects.create(
                    chat=chat,
                    user=target,
                    text=f"Hey {user.username}, how are you?"
                )
                Message.objects.create(
                    chat=chat,
                    user=user,
                    text=f"Hi {target.username}! I'm doing well, let's chat."
                )
            else:
                # If chat exists, just add one more message to make it active
                Message.objects.create(
                    chat=chat,
                    user=user,
                    text=f"Updating chat at {timezone.now()}"
                )

    # Create a few global group chats
    group_names = ["Global Lounge", "Tech Talk", "Random Stuff"]
    for g_name in group_names:
        chat, created = Chat.objects.get_or_create(
            name=g_name.lower().replace(" ", "-")[:20],
            defaults={'description': f'Public group: {g_name}'}
        )
        if created:
            # Add all users to group chats
            chat.participants.add(*users)
            print(f"Created group chat: {g_name}")
            
            Message.objects.create(
                chat=chat,
                text=f"Welcome to {g_name} everyone!"
            )

    print("Data generation for all users complete.")

if __name__ == "__main__":
    generate_data_for_all_users()
