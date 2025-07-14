from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import BadSignature
from django.http import HttpResponse
from django.db.models import Prefetch, Q
from Admin.models import *
from Guest.models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
import random
from django.urls import reverse
from django.core.signing import Signer 



# Create your views here.
def login(request):
    if request.method == "POST":
        email = request.POST.get("txt_email")
        password = request.POST.get("txt_pass")

        # Admin login (assuming it's still using plaintext password)
        admincount = tbl_admin.objects.filter(admin_email=email, admin_password=password).count()

        # User login with hashed password
        try:
            userdata = tbl_newuser.objects.get(user_email=email)
            if check_password(password, userdata.user_password):  # ✅ Compare hashed
                if userdata.verify_status == 2:
                    request.session['uid'] = userdata.id
                    return redirect('wuser:userhomepage')
                else:
                    msg = "Your account is not yet verified. Please check your email or contact support."
                    return render(request, 'Guest/LoginSignup.html', {'msg': msg, 'show_signup': False})
            else:
                msg = "Invalid credentials!!"
                return render(request, 'Guest/LoginSignup.html', {'msg': msg, 'show_signup': False})
        except tbl_newuser.DoesNotExist:
            pass

        # Admin login success
        if admincount > 0:
            admindata = tbl_admin.objects.get(admin_email=email, admin_password=password)
            request.session['aid'] = admindata.id
            return redirect('wadmin:homepage')

        # If nothing matched
        msg = "Invalid credentials!!"
        return render(request, 'Guest/LoginSignup.html', {'msg': msg, 'show_signup': False})

    return render(request, 'Guest/LoginSignup.html')



def signup(request):
    if request.method == "POST":
        email = request.POST.get("txt_email")

        if tbl_newuser.objects.filter(user_email=email).exists():
            return render(request, 'Guest/LoginSignup.html', {
                'msg': "Email already exists!",
                'show_signup': True 
            })

        # ✅ Hash the password here
        hashed_password = make_password(request.POST.get("txt_password"))

        new_user = tbl_newuser.objects.create(
            user_firstname=request.POST.get("txt_fname"),
            user_lastname=request.POST.get("txt_lname"),
            user_email=email,
            user_phone='+' + request.POST.get("country_code") + request.POST.get("txt_phone"),
            user_password=hashed_password,  # ✅ Save hashed password
            user_gender=request.POST.get("txt_gender"),
            verify_status=0  # Only set as unverified on signup
        )

        try:
            signer = Signer()
            signed_user_id = signer.sign(new_user.id)

            verify_url = request.build_absolute_uri(
                reverse('wguest:verify_email', args=[signed_user_id])
            )

            email_body = f"""
Hi {new_user.user_firstname},<br><br>
Thanks for signing up with <b>WarmNest</b>! 🎉<br><br>
Click the button below to verify your email:<br><br>
<a href="{verify_url}" style="padding: 10px 15px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Confirm Email</a><br><br>
If you didn't register, please ignore this message.<br><br>
Warm regards,<br>  
Team WarmNest
"""

            send_mail(
                subject='Confirm your email - WarmNest',
                message='Please confirm your email.',
                html_message=email_body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

        except Exception as e:
            print(f"Email sending failed: {e}")

        return render(request, 'Guest/LoginSignup.html', {
            'msg': "Signup successful. Please check your email to verify your account."
        })

    return render(request, 'Guest/LoginSignup.html')


def verify_email(request, signed_user_id):
    signer = Signer()
    try:
        user_id = signer.unsign(signed_user_id)
        user = tbl_newuser.objects.get(id=user_id)
        user.verify_status = 1  # Verified only here
        user.save()

        return HttpResponse("Email verified successfully! You may now log in.")
    except (BadSignature, tbl_newuser.DoesNotExist):
        return HttpResponse("Invalid or expired verification link.")


def homepage(request):
    properties = tbl_property.objects.prefetch_related(
        Prefetch('gallery_images', to_attr='images')
    )
    return render(request, "Guest/HomePage.html", {
        'properties': properties
    })

def viewproperty(request):
    property_types = []
    selected_property_types = []
    search_query = ''
    room_size = rent_type = bills_included = is_en_suite = short_term = room_furnishing = ''
    share_occupation = room_for = share_gender = household_option = property_habit = current_status = ''
    min_price = max_price = ''

    property_qs = tbl_property.objects.all()
    if request.method == "GET":
        search_query = request.GET.get('search_query', '').strip()
        if search_query:
            property_qs = property_qs.filter(postcode__icontains=search_query)
    if request.method == "POST":
        property_types = request.POST.getlist('property_type')
        selected_property_types = property_types
        search_query = request.POST.get('search_query', '').strip()
        room_size = request.POST.get('room_size')
        rent_type = request.POST.get('rent_type')
        bills_included = request.POST.get('bills_included')
        is_en_suite = request.POST.get('is_en_suite')
        short_term = request.POST.get('short_term')
        room_furnishing = request.POST.get('room_furnishing')
        share_occupation = request.POST.get('share_occupation')
        room_for = request.POST.get('room_for')
        share_gender = request.POST.get('share_gender')
        household_option = request.POST.get('household_option')
        property_habit = request.POST.get('property_habit')
        current_status = request.POST.get('current_status')
        min_price = request.POST.get('min_price')
        max_price = request.POST.get('max_price')

        if property_types:
            property_qs = property_qs.filter(property_type__in=property_types)
        if search_query:
            property_qs = property_qs.filter(postcode__icontains=search_query)
        if min_price:
            property_qs = property_qs.filter(rate_or_price__gte=min_price)
        if max_price:
            property_qs = property_qs.filter(rate_or_price__lte=max_price)
        if room_size:
            property_qs = property_qs.filter(room_size=room_size)
        if rent_type:
            property_qs = property_qs.filter(rent_type=rent_type)
        if bills_included:
            property_qs = property_qs.filter(bills_included=(bills_included == 'true'))
        if is_en_suite:
            property_qs = property_qs.filter(is_en_suite=(is_en_suite == 'true'))
        if short_term:
            property_qs = property_qs.filter(short_term=(short_term == 'true'))
        if room_furnishing:
            property_qs = property_qs.filter(room_furnishing=room_furnishing)
        if share_occupation:
            property_qs = property_qs.filter(share_occupation=share_occupation)
        if room_for:
            property_qs = property_qs.filter(room_for=room_for)
        if share_gender:
            property_qs = property_qs.filter(share_gender=share_gender)
        if household_option:
            property_qs = property_qs.filter(household_option=household_option)
        if property_habit:
            property_qs = property_qs.filter(property_habit=property_habit)
        if current_status:
            property_qs = property_qs.filter(current_status=current_status)

    property_qs = property_qs.prefetch_related(
        Prefetch('gallery_images', queryset=tbl_gallery.objects.order_by('id'), to_attr='images')
    )

    paginator = Paginator(property_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "Guest/ViewProperty.html", {
        "properties": page_obj.object_list,
        "page_obj": page_obj,
        "search_query": search_query,
        "selected_property_types": selected_property_types,
    })

def viewdetails(request, property_id): 
    property = get_object_or_404(tbl_property, pk=property_id)
    user_id = request.session.get('uid')
    user = None
    is_favorited = False

    if user_id:
        user = get_object_or_404(tbl_newuser, pk=user_id)
        is_favorited = tbl_favourite.objects.filter(user=user, property=property).exists()

        if request.method == 'POST' and 'favorite' in request.POST:
            if is_favorited:
                tbl_favourite.objects.filter(user=user, property=property).delete()
            else:
                tbl_favourite.objects.create(user=user, property=property)
            return redirect('wguest:viewdetails', property_id=property.id)

    gallery_images = tbl_gallery.objects.filter(property=property)

    return render(request, 'Guest/ViewDetailsProperty.html', {
        'property': property,
        'user': user,
        'gallery_images': gallery_images,
        'is_favorited': is_favorited,
    })

def forget_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = tbl_newuser.objects.get(user_email=email)
            otp = str(random.randint(1000, 9999))
            request.session["reset_email"] = email
            request.session["reset_otp"] = otp

            send_mail(
                subject='Password Reset OTP - WarmNest',
                message=f'Your OTP for resetting your password is: {otp}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect("wguest:verify_otp")
        except tbl_newuser.DoesNotExist:
            return render(request, "Guest/ForgetPassword.html", {"error": "Email does not exist"})
    return render(request, "Guest/ForgetPassword.html")

def verify_otp_view(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = request.session.get("reset_otp")

        if entered_otp == session_otp:
            return redirect("wguest:reset_password")
        else:
            return render(request, "Guest/VerifyOTP.html", {"error": "Invalid OTP. Please try again."})
    return render(request, "Guest/VerifyOTP.html")



def create_new_password_view(request):
    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.session.get("reset_email")

        if new_password != confirm_password:
            return render(request, "Guest/CreateNewPassword.html", {"error": "Passwords do not match"})

        try:
            user = tbl_newuser.objects.get(user_email=email)
            user.user_password = make_password(new_password)  # ✅ Hash the new password
            user.save()
            del request.session['reset_email']
            del request.session['reset_otp']
            return redirect("wguest:login")
        except tbl_newuser.DoesNotExist:
            return render(request, "Guest/CreateNewPassword.html", {"error": "User not found"})

    return render(request, "Guest/CreateNewPassword.html")
