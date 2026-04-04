# Create your views here.
from django.shortcuts import render,redirect
from django.contrib import messages
from users.models import UserRegistrationModel


# Create your views here.
def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)
        if usrid == 'Mahesh' and pswd == 'admin123':
            request.session['admin_id'] = 'Mahesh'
            request.session['user_type'] = 'admin'
            messages.success(request, "Welcome back, Admin!")
            return redirect('adminhome')

        else:
            messages.error(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html', {})



def RegisterUsersView(request):
    if 'admin_id' not in request.session or request.session.get('user_type') != 'admin':
        messages.error(request, "Admin access required.")
        return redirect('AdminLogin')
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/viewregisterusers.html', context={'data': data})




def ActivaUsers(request):
    if 'admin_id' not in request.session or request.session.get('user_type') != 'admin':
        messages.error(request, "Admin access required.")
        return redirect('AdminLogin')
    if request.method == 'GET':
        user_id = request.GET.get('uid')
        
        if user_id:  # Ensure user_id is not None
            status = 'activated'
            print("Activating user with ID =", user_id)
            UserRegistrationModel.objects.filter(id=user_id).update(status=status)

        # Redirect to the view where users are listed after activation
        return redirect('RegisterUsersView')  # Replace with your actual URL name

def DeactivateUsers(request):
    if 'admin_id' not in request.session or request.session.get('user_type') != 'admin':
        messages.error(request, "Admin access required.")
        return redirect('AdminLogin')
    if request.method == 'GET':
        user_id = request.GET.get('uid')
        
        if user_id:
            status = 'waiting'
            print("Deactivating user with ID =", user_id)
            UserRegistrationModel.objects.filter(id=user_id).update(status=status)

        return redirect('RegisterUsersView')

def DeleteUsers(request):
    if 'admin_id' not in request.session or request.session.get('user_type') != 'admin':
        messages.error(request, "Admin access required.")
        return redirect('AdminLogin')
    if request.method == 'GET':
        user_id = request.GET.get('uid')
        
        if user_id:  # Ensure user_id is not None
            print("Deleting user with ID =", user_id)
            UserRegistrationModel.objects.filter(id=user_id).delete()

        # Redirect to the view where users are listed after deletion
        return redirect('RegisterUsersView')  # Replace with your actual URL name

def adminhome(request):
    if 'admin_id' not in request.session or request.session.get('user_type') != 'admin':
        messages.error(request, "Admin access required.")
        return redirect('AdminLogin')
    return render(request, 'admins/AdminHome.html')