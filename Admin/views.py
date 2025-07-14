from django.shortcuts import render,redirect
from Admin.models import *
from Guest.models import *
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.db.models import OuterRef, Subquery
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

# Create your views here.
from django.db.models import Count

def HomePage(request):
    if not request.session.get('aid'):
        return redirect('wguest:login')

    # Total Verified Users (verify_status=2)
    total_users = tbl_newuser.objects.filter(verify_status=2).count()

    # Total Properties
    total_properties = tbl_property.objects.count()

    # New Registrations (verify_status=1)
    new_registrations = tbl_newuser.objects.filter(verify_status=1).count()

    # Total Inquiries (count of unique property-user pairs)
    total_inquiries = tbl_message.objects.values('sender', 'property').distinct().count()

    # Pending Messages (is_from_admin=0 and status='pending')
    pending_msg = tbl_message.objects.filter(is_from_admin=False, status='pending').count()

    # Available Properties (current_status='available')
    available_properties = tbl_property.objects.filter(current_status='available').count()

    # Most Saved Property (by favourites)
    favourite_counts = tbl_favourite.objects.values('property').annotate(total=Count('property')).order_by('-total')
    most_saved_property = None
    if favourite_counts.exists():
        top_property_id = favourite_counts.first()['property']
        most_saved_property = tbl_property.objects.get(id=top_property_id)

    return render(request, "Admin/HomePage.html", {
        'total_users': total_users,
        'total_properties': total_properties,
        'new_registrations': new_registrations,
        'total_inquiries': total_inquiries,
        'pending_msg': pending_msg,
        'available_properties': available_properties,
        'most_saved_property': most_saved_property
    })
 


def View_Message(request):
    if not request.session.get('aid'):
        return redirect('wguest:login')
    """
    All user messages still waiting for an admin reply (status='pending').
    Show newest first.
    """
    messages = (tbl_message.objects
                .filter(is_from_admin=False, status='pending')
                .select_related('sender', 'house', 'room')
                .order_by('-created_at'))
    return render(request,'Admin/ViewMessages.html',{'messages': messages})


def view_property(request):
    if not request.session.get('aid'):
        return redirect('wguest:login')
    # Default to 'all' if no filter is selected
    filter_type = request.POST.get('filter_type', 'all')

    if filter_type == 'all':
        properties = tbl_property.objects.all()
    else:
        properties = tbl_property.objects.filter(property_type=filter_type)

    return render(request, "Admin/ViewProperty.html", {
        "properties": properties
    })

def Add_Property(request):
    if request.method == "POST":
       
        bills_included = request.POST.get("bills_included") == "on"
        short_term = request.POST.get("short_term") == "on"
        is_en_suite = request.POST.get("is_en_suite") == "on"

        
        preferences = ','.join(request.POST.getlist('property_preference'))

        property = tbl_property.objects.create(
            title=request.POST.get("title"),
            address=request.POST.get("address"),
            postcode=request.POST.get("postcode"),
            rate=request.POST.get("rate"),
            rent_type=request.POST.get("rent_type"),
            bills_included=bills_included,
            available_from=request.POST.get("available_from"),
            available_to=request.POST.get("available_to"),
            min_stay=request.POST.get("min_stay"),
            max_stay=request.POST.get("max_stay"),
            days_available=request.POST.get("days_available"),
            short_term=short_term,
            property_type=request.POST.get("property_type"),
            room_size=request.POST.get("room_size"),
            room_furnishing=request.POST.get("room_furnishing"),
            is_en_suite=is_en_suite,
            no_of_rooms=request.POST.get("no_of_rooms"),
            share_occupation=request.POST.get("share_occupation"),
            room_for=request.POST.get("room_for"),
            share_gender=request.POST.get("share_gender"),
            occupant_age=request.POST.get("occupant_age"),
            household_option=request.POST.get("household_option"),
            no_of_bedrooms=request.POST.get("no_of_bedrooms"),
            property_preference=preferences,
            property_habit=request.POST.get("property_habit"),
            room_suitable_for=request.POST.get("room_suitable_for"),
            current_status=request.POST.get("current_status"),
        )

        images = request.FILES.getlist("txt_images")
        for img in images:
            tbl_gallery.objects.create(property=property, image=img)

        return redirect('wadmin:addproperty')

    return render(request, 'Admin/AddProperty.html')


def view_more(request, property_id):
    if not request.session.get('aid'):
        return redirect('wguest:login')
    property = get_object_or_404(tbl_property, pk=property_id)
    edit = request.GET.get('edit') == 'true'

    user = request.user

    if request.method == 'POST':
        if 'delete' in request.POST:
            tbl_message.objects.filter(property=property).delete()
            tbl_gallery.objects.filter(property=property).delete()
            property.delete()
            messages.success(request, "Property deleted successfully.")
            return redirect('wadmin:viewproperty')

        # Update property fields
        property.title = request.POST.get('title')
        property.address = request.POST.get('address')
        property.postcode = request.POST.get('postcode')
        property.rate = request.POST.get('rate')
        property.rent_type = request.POST.get('rent_type')
        property.current_status = request.POST.get('current_status')
        property.bills_included = 'bills_included' in request.POST
        property.available_from = request.POST.get('available_from')
        property.available_to = request.POST.get('available_to')
        property.min_stay = request.POST.get('min_stay')
        property.max_stay = request.POST.get('max_stay')
        property.days_available = request.POST.get('days_available')
        property.short_term = 'short_term' in request.POST
        property.property_type = request.POST.get('property_type')
        property.room_size = request.POST.get('room_size')
        property.room_furnishing = request.POST.get('room_furnishing')
        property.is_en_suite = 'is_en_suite' in request.POST
        property.no_of_rooms = request.POST.get('no_of_rooms')
        property.share_occupation = request.POST.get('share_occupation')
        property.room_for = request.POST.get('room_for')
        property.share_gender = request.POST.get('share_gender')
        property.occupant_age = request.POST.get('occupant_age')
        property.household_option = request.POST.get('household_option')
        property.no_of_bedrooms = request.POST.get('no_of_bedrooms')
        property.property_preference = ",".join(request.POST.getlist('property_preference'))
        property.property_habit = request.POST.get('property_habit')
        property.room_suitable_for = request.POST.get('room_suitable_for')
        property.save()

        #Update existing images if replaced
        for gallery_image in property.gallery_images.all():
            image_field_name = f'update_image_{gallery_image.id}'
            if image_field_name in request.FILES:
                gallery_image.image = request.FILES[image_field_name]
                gallery_image.save()

        #Add new images
        new_images = request.FILES.getlist('txt_images[]')
        for img_file in new_images:
            tbl_gallery.objects.create(
                property=property,
                image=img_file
            )
        #to delete image
        deleted_ids = request.POST.get('deleted_images')
        if deleted_ids:
            ids_to_delete = [int(i) for i in deleted_ids.split(",") if i]
            tbl_gallery.objects.filter(id__in=ids_to_delete, property=property).delete()

        messages.success(request, "Property updated successfully.")
        return redirect('wadmin:viewmore', property_id=property.id)

    # Stay options
    stay_options = [
        ("0", "Any"),
        ("1", "1 month"),
        ("2", "2 months"),
        ("3", "3 months"),
        ("4", "4 months"),
        ("5", "5 months"),
        ("6", "6 months"),
        ("7", "7 months"),
        ("8", "8 months"),
        ("9", "9 months"),
        ("10", "10 months"),
        ("11", "11 months"),
        ("12", "1 year"),
        ("15", "1 year 3 months"),
        ("18", "1 year 6 months"),
        ("21", "1 year 9 months"),
        ("24", "2 years"),
    ]

    return render(request, 'Admin/ViewMore.html', {
        'property': property,
        'edit': edit,
        'stay_options': stay_options,
    })




def User_List(request):
    if not request.session.get('aid'):
        return redirect('wguest:login')
    query = request.GET.get('q', '')

    # Filter only verified users
    user_list = tbl_newuser.objects.filter(verify_status=1)

    # Filter by email or phone if query is present
    if query:
        user_list = user_list.filter(
            Q(user_email__icontains=query) |
            Q(user_phone__icontains=query)
        )

    paginator = Paginator(user_list, 10)
    page_number = request.GET.get('page')
    items = paginator.get_page(page_number)

    return render(request, 'Admin/NewUsers.html', {
        'items': items,
        'query': query,
    })


def verifyuser(request, id):
    if not request.session.get('aid'):
        return redirect('wguest:login')
    user = get_object_or_404(tbl_newuser, id=id)
    user.verify_status = 2
    user.verification_time = timezone.now() 
    user.save()
    return redirect('wadmin:userlist') 

def rejectuser(request, id):
    if not request.session.get('aid'):
        return redirect('wguest:login')
    user = get_object_or_404(tbl_newuser, id=id)
    user.verify_status = 3
    user.verification_time = timezone.now() 
    user.save()
    return redirect('wadmin:userlist') 


def verified_users(request):
    if not request.session.get('aid'):
        return redirect('wguest:login')
    query = request.GET.get('q', '')
    date_filter = request.GET.get('date', '')

    # Base queryset: only verified users
    user_list = tbl_newuser.objects.filter(verify_status=2)

    # Apply filters if any
    if query:
        user_list = user_list.filter(user_email__icontains=query)
    if date_filter:
        user_list = user_list.filter(verification_time__date=date_filter)  # or use a `verified_at` field if available

    paginator = Paginator(user_list.order_by('-verification_time'), 5)
    page_number = request.GET.get('page', 1)
    users = paginator.get_page(page_number)

    return render(request, 'Admin/VerifiedUsers.html', {
        'users': users,
        'query': query,
        'date_filter': date_filter
    })

def blocked_users(request):
    query = request.GET.get('q', '')            # Email search
    date_filter = request.GET.get('date', '')   # Rejected date filter

    # Base queryset: only blocked users
    user_list = tbl_newuser.objects.filter(verify_status=3)

    # Apply filters
    if query:
        user_list = user_list.filter(user_email__icontains=query)
    if date_filter:
        user_list = user_list.filter(verification_time__date=date_filter)

    # Pagination
    paginator = Paginator(user_list.order_by('-verification_time'), 5)
    page_number = request.GET.get('page', 1)
    users = paginator.get_page(page_number)

    return render(request, 'Admin/BlockedUsers.html', {
        'users': users,
        'query': query,
        'date_filter': date_filter
    })

def pending_user_messages(request):
    if not request.session.get('aid'):
        return redirect('wguest:login')
    seen_pairs = set()
    latest_messages = []

    
    all_messages = tbl_message.objects.filter(
        status='pending',
        is_from_admin=False
    ).select_related('sender', 'property').order_by('-created_at')

    for msg in all_messages:
        key = (msg.sender_id, msg.property_id)
        if key not in seen_pairs:
            latest_messages.append(msg)
            seen_pairs.add(key)

    return render(request, 'Admin/PendingMessages.html', {
        'messages': latest_messages
    })

def message_reply(request, user_id, property_id):
    if not request.session.get('aid'):
        return redirect('wguest:login')

    user = get_object_or_404(tbl_newuser, pk=user_id)
    property_obj = get_object_or_404(tbl_property, pk=property_id)

    # Mark all unread messages from this user for this property as read when admin opens the chat
    tbl_message.objects.filter(
        sender=user,
        property=property_obj,
        is_from_admin=False,
        is_read=0
    ).update(is_read=1)

    return render(request, 'Admin/ReplyMessage.html', {
        'user': user,
        'property': property_obj
    })


def replied_messages(request):
    if not request.session.get('aid'):
        return redirect('wguest:login')

    query = request.GET.get('q', '')
    property_query = request.GET.get('property', '')

   
    latest = tbl_message.objects.filter(
        sender=OuterRef('sender'),
        property=OuterRef('property'),
        is_from_admin=True,
        status='replied'
    ).order_by('-created_at')

    # Main query
    messages = tbl_message.objects.filter(
        pk=Subquery(latest.values('pk')[:1])
    ).select_related('sender', 'property')

    
    if query:
        messages = messages.filter(sender__user_firstname__icontains=query)
    if property_query:
        messages = messages.filter(property__title__icontains=property_query)

    
    messages = messages.order_by('-created_at')
    paginator = Paginator(messages, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Admin/RepliedMessages.html', {
        'messages': page_obj,
        'query': query,
        'property_query': property_query,
    })

def admin_logout(request):
    request.session.flush()
    return redirect('wguest:login')