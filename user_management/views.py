from irasusapp.models import Crmuser
from .forms import UserCreatedByAdmin
from django.shortcuts import render, redirect

# Create your views here.

def addUser(request):
    form = UserCreatedByAdmin()
    if request.method == "POST":
        form = UserCreatedByAdmin(request.POST)
        if form.is_valid():
            form.save()
    context = { 'form': form }
    return render(request,'user_management_templates/user_add.html',context)


def getUser(request):
    if request.method == "GET":
        data = list(Crmuser.objects.values())
        print(data, "[][][][][][][][")
    contex = {'user_data' : data }
    return render(request, 'user_management_templates/get_userdata.html',contex)


def updateUser(request,id):
    if request.method == 'POST':
        print("IF IN THIS CONDITION ")
        pi = Crmuser.objects.get(pk=id)
        print(pi, "=====PI=========================")
        fm = UserCreatedByAdmin(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
    else:
        pi = Crmuser.objects.get(pk=id)
        print(pi, "ELSE PI=========><><><><>")
        fm = UserCreatedByAdmin(instance=pi)
    return render(request,'user_management_templates/update_user.html',{'form': fm})


def deleteUser(request, id):
    try:
        pi = Crmuser.objects.get(pk=id)
        print(pi, "++++++INSTANCE=====")
        if request.method == 'POST':
            print("IF IN THE POST")
            pi.delete()
            return redirect('user_management:getdata')
        context = {}
        return render(request, "user_management_templates/get_userdata.html", context)
    except Exception as e:
        print("Error While deleting Record",e)
