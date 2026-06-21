from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, UserProfile

@receiver(post_save, sender=Order)
def update_user_spent_and_bonus(sender, instance, **kwargs):
    print(f"\n=== SIGNAL CALLED for Order {instance.id} ===")
    print(f"Status: {instance.status}, User: {instance.user}")
    
    if kwargs.get('update_fields') == ['bonus_points_earned']:
        print("Skipping recursive save")
        return

    if instance.status == 'completed' and instance.user:
        profile, created = UserProfile.objects.get_or_create(user=instance.user)
        print(f"Profile: {profile.user.username}, current bonus_points: {profile.bonus_points}, total_spent: {profile.total_spent}")
        
        profile.total_spent += instance.total_price
        earned = int(instance.total_price / 100)
        print(f"Earned: {earned} (from {instance.total_price})")
        
        if earned > 0:
            profile.bonus_points += earned
            print(f"New bonus_points: {profile.bonus_points}")
            # Сигналсыз жаңарту
            Order.objects.filter(pk=instance.pk).update(bonus_points_earned=earned)
        
        profile.save()
        print(f"Profile saved. Now bonus_points={profile.bonus_points}, total_spent={profile.total_spent}")
    else:
        print("Status not completed or no user")