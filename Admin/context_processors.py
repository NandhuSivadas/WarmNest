from .models import tbl_message, tbl_admin

def pending_messages(request):
    pending_messages = []
    admin_name = None
    admin_email = None

    if request.session.get('aid'):
        # Fetch admin details
        try:
            admin = tbl_admin.objects.get(id=request.session['aid'])
            admin_name = admin.admin_name
            admin_email = admin.admin_email
        except tbl_admin.DoesNotExist:
            pass  # in case somehow session has invalid id

        # Fetch unread messages
        seen_pairs = set()
        all_messages = tbl_message.objects.filter(
            is_read=0,
            is_from_admin=0
        ).select_related('sender', 'property').order_by('-created_at')

        for msg in all_messages:
            key = (msg.sender_id, msg.property_id)
            if key not in seen_pairs:
                pending_messages.append(msg)
                seen_pairs.add(key)

    return {
        'pending_messages': pending_messages,
        'admin_name': admin_name,
        'admin_email': admin_email
    }
