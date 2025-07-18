from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Q
from django.http import Http404
from Admin import admin
from Admin.models import *
from Guest.models import *
from django.db.models import Max
import traceback
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password, make_password
from User.models import*



#Machine learning model required libraries
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer


def userhomepage(request):
    if not request.session.get('uid'):
        return redirect('wguest:login')
    properties = tbl_property.objects.prefetch_related(
        Prefetch('gallery_images', to_attr='images')  # 'images' will hold the list of gallery objects
    )

    return render(request, 'User/UserHomePage.html', {
        'properties': properties
    })


def my_profile(request):
    if not request.session.get('uid'):
        return redirect('wguest:login')
    user=tbl_newuser.objects.get(id=request.session['uid'])
    return render(request,'User/MyProfile.html',{'user':user})


def edit_profile(request):
    if not request.session.get('uid'):
        return redirect('wguest:login')
    user = tbl_newuser.objects.get(id=request.session['uid'])
    
    if request.method == "POST":
        user.user_firstname = request.POST.get("txt_firstname")
        user.user_lastname = request.POST.get("txt_lastname")
        user.user_email = request.POST.get("txt_email")
        
        country_code = request.POST.get("country_code", "").strip()
        contact_number = request.POST.get("txt_contact", "").strip()
        full_phone = f"+{country_code}{contact_number}"
        user.user_phone = full_phone
        
        user.user_gender = request.POST.get("txt_gender")
        user.save()
        return render(request, 'User/MyProfile.html', {'user': user})
    
   
    full_phone = user.user_phone or ""
    if full_phone.startswith("+") and len(full_phone) > 10:
        country_code = full_phone[1:-10]
        contact_number = full_phone[-10:]
    else:
        country_code = ""
        contact_number = ""

    return render(request, 'User/EditProfile.html', {
        'user': user,
        'country_code': country_code,
        'contact_number': contact_number,
    })


def change_password(request):
    if not request.session.get('uid'):
        return redirect('wguest:login')

    user = tbl_newuser.objects.get(id=request.session['uid'])

    if request.method == "POST":
        currentpass = request.POST.get("txt_currentpassword")
        newpass = request.POST.get("txt_newpassword")
        conpass = request.POST.get("txt_confirmpassword")

        # Compare hashed current password
        if check_password(currentpass, user.user_password):
            if newpass == conpass:
                # Hash the new password before saving
                user.user_password = make_password(newpass)
                user.save()
                msg = "Password changed successfully"
            else:
                msg = "New passwords do not match"
        else:
            msg = "Current password is incorrect"

        return render(request, 'User/ChangePassword.html', {'msg': msg})

    return render(request, 'User/ChangePassword.html')

    
    
def messageuser(request, property_id=None):
    if not request.session.get('uid'):
        return redirect('wguest:login')

    user_id = request.session.get('uid')
    if not user_id:
        return redirect('wguest:login')
    
    

    # Validate user
    user = get_object_or_404(tbl_newuser, pk=user_id)

    # Validate property
    if not property_id:
        raise Http404("No property specified.")
    property_obj = get_object_or_404(tbl_property, pk=property_id)

    tbl_message.objects.filter(
       sender=user_id,
       property=property_obj,
      is_from_admin=True,
      is_read=0
    ).update(is_read=1)
    # Role is 'user'
    role = 'user'

    context = {
        'user': user,
        'property': property_obj,
        'user_id': user.id,
        'property_id': property_obj.id,
        'role': role
    }

    # Important: render to 'MessageUser.html'
    return render(request, "User/MessageUser.html", context)

#Recommendation
def get_similar_properties(target_property, n_neighbors=3):
    all_properties = tbl_property.objects.exclude(id=target_property.id)
    if not all_properties:
        return []

    data = pd.DataFrame(list(all_properties.values(
        'id', 'rate', 'no_of_bedrooms', 'property_type', 'room_size'
    )))

    target_data = pd.DataFrame([{
        'id': target_property.id,
        'rate': target_property.rate,
        'no_of_bedrooms': target_property.no_of_bedrooms,
        'property_type': target_property.property_type,
        'room_size': target_property.room_size
    }])

    combined_data = pd.concat([data, target_data], ignore_index=True)

    
    numeric_features = ['rate', 'no_of_bedrooms']
    categorical_features = ['property_type', 'room_size']


    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

    X = preprocessor.fit_transform(combined_data.drop('id', axis=1))

    knn = NearestNeighbors(n_neighbors=n_neighbors + 1)
    knn.fit(X)
    distances, indices = knn.kneighbors([X[-1]])
    similar_indices = indices[0][1:]
    similar_ids = combined_data.iloc[similar_indices]['id'].tolist()

    return tbl_property.objects.filter(id__in=similar_ids)

def viewproperty(request):
    if not request.session.get('uid'):
        return redirect('wguest:login')
    # Initialize all filter variables
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
        # Fetch values from form
        property_types = request.POST.getlist('property_type')
        selected_property_types = property_types  # assign it here
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

        # Apply filters
        if property_types:
            property_qs = property_qs.filter(property_type__in=property_types)
        if search_query:
            property_qs = property_qs.filter(postcode__icontains=search_query)
        if min_price:
            property_qs = property_qs.filter(rate__gte=min_price)
        if max_price:
            property_qs = property_qs.filter(rate__lte=max_price)
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

    # Prefetch gallery images for all cases
    property_qs = property_qs.prefetch_related(
        Prefetch('gallery_images', queryset=tbl_gallery.objects.order_by('id'), to_attr='images')
    )

    # Pagination: 12 properties per page
    paginator = Paginator(property_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "User/ViewProperty.html", {
        "properties": page_obj.object_list,  # Properties for the current page
        "page_obj": page_obj,                # Full page object for pagination links
        "search_query": search_query,
        "selected_property_types": selected_property_types,
    })



def viewdetails(request, property_id):
    if not request.session.get('uid'):
        return redirect('wguest:login')

    property = get_object_or_404(tbl_property, pk=property_id)
    user_id = request.session.get('uid')
    user = get_object_or_404(tbl_newuser, pk=user_id) if user_id else None
    is_favorited = tbl_favourite.objects.filter(user=user, property=property).exists() if user else False

    if request.method == 'POST' and 'favorite' in request.POST:
        if is_favorited:
            tbl_favourite.objects.filter(user=user, property=property).delete()
        else:
            tbl_favourite.objects.create(user=user, property=property)
        return redirect('wuser:viewdetails', property_id=property.id)

    gallery_images = tbl_gallery.objects.filter(property=property)

    similar_properties = get_similar_properties(property).prefetch_related(
        Prefetch('gallery_images', queryset=tbl_gallery.objects.order_by('id'), to_attr='images')
    )

    return render(request, 'User/ViewDetailsProperty.html', {
        'property': property,
        'user': user,
        'gallery_images': gallery_images,
        'is_favorited': is_favorited,
        'similar_properties': similar_properties,
    })


def mymessages(request):
    if not request.session.get('uid'):
        return redirect('wguest:login')
    uid = request.session.get('uid')
    if not uid:
        return render(request, 'login.html')

    # Get latest message id for each property sent by this user
    latest_messages = tbl_message.objects.filter(sender_id=uid).values('property_id').annotate(
        latest_message_id=Max('id')
    )

    latest_message_ids = [item['latest_message_id'] for item in latest_messages]

    messages = tbl_message.objects.filter(id__in=latest_message_ids).select_related('property').order_by(
        '-is_from_admin', 'is_read', '-created_at'
    )

    context = {
        'messages': messages
    }

    return render(request, 'User/MyMessages.html', context)

def add_to_favourites(request, property_id):
    if not request.session.get('uid'):
        return redirect('wguest:login')
    property = get_object_or_404(tbl_property, pk=property_id)
    user= request.session.get('uid')

    tbl_favourite.objects.get_or_create(user=user, property=property)
    return redirect('wuser:viewproperty')  # or redirect to 'wadmin:viewmore' if needed


def favourite_list(request):
    if not request.session.get('uid'):
        return redirect('wguest:login')
    user_id = request.session.get('uid')
    favourites = tbl_favourite.objects.filter(user=user_id).select_related('property')

    # Attach gallery images to each property
    for fav in favourites:
        fav.property.images = tbl_gallery.objects.filter(property_id=fav.property.id)

    return render(request, 'User/Favourites.html', {'favourites': favourites})
 
def user_logout(request):
    request.session.flush()
    return redirect('wguest:login')

@require_http_methods(["GET", "POST"])
def logout_confirm(request):
        if request.method == "POST":
            action = request.POST.get("confirm")
            if action == "yes":
                user_logout(request)
                return redirect("wuser:userhomepage")        # or wherever you land guests
            else:
                # 'No' pressed – go back to previous page or homepage
                return redirect(request.POST.get("next") or "wuser:userhomepage")

        # GET: render the page
        next_url = request.GET.get("next", "")
        return render(request,'User/LogoutConfirmation.html',{"next": next_url})

def user_review(request,property_id):
    if not request.session.get('uid'):
        return redirect('wguest:login')
    user_id = request.session.get('uid')
    user = get_object_or_404(tbl_newuser, id=user_id)
    property=get_object_or_404(tbl_property,id=property_id)
    if request.method == 'POST':
        review_text = request.POST.get('review')
        if review_text:
            tbl_review.objects.create(
                review=review_text,
                user=user,
                property=property,
            )
            return redirect('wuser:viewdetails', property_id)  # Redirect to property detail page

    return render(request, 'User/Review.html', {
        'property': property,
    })



