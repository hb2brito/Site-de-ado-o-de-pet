from django.shortcuts import render, redirect
from divulgar.models import Pet, Raca
from .models import PedidoAdocao
from datetime import datetime
from django.contrib.messages import constants
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def listar_pets(request):
    if request.user.is_authenticated:
        nome= request.user.username
        
    if request.method == "GET":
        cidade = request.GET.get('cidade')
        raca_filter = request.GET.get('raca')
        pets = Pet.objects.filter(status="P")
        racas = Raca.objects.all()
        usuarios_filter = request.GET.get('username')
        usuarios= User.objects.all()
        
        if cidade:
            pets = pets.filter(cidade__icontains=cidade)

        if raca_filter:
            pets = pets.filter(raca__id=raca_filter)
            raca_filter = Raca.objects.get(id=raca_filter)

        if usuarios_filter:
            pets = pets.filter(usuario_id= usuario_filter)
            usuario_filter= User.objects.get(id=usuario_filter)



        return render(request,'listar_pets.html',{'pets': pets, 'racas': racas, 'cidade': cidade, 'raca_filter': raca_filter, 'nome':nome})

@login_required   
def pedido_adocao(request, id_pet):
    # Verificar se o usuario é dono do pet
    pet = Pet.objects.filter(id=id_pet).filter(usuario=request.user)
    if pet.exists():
        messages.add_message(request, constants.ERROR, 'Você não pode adotar seu próprio pet')
        return redirect('/divulgar/seus_pets')

    pet = Pet.objects.filter(id=id_pet).filter(status="P")
    if not pet.exists():
        messages.add_message(request, constants.ERROR, 'Esse pet já foi adotado :)')
        return redirect('/adotar')
    
    pedido = PedidoAdocao.objects.filter(pet=pet.first()).filter(usuario=request.user)
    if pedido.exists():
        messages.add_message(request, constants.ERROR, 'Você já fez um pedido de adoção para esse pet')
        return redirect('/adotar')
    
    
    pedido = PedidoAdocao(pet=pet.first(),
                          usuario=request.user,
                          data=datetime.now())
    
    pedido.save()
    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção realizado, você receberá um e-mail caso ele seja aprovado.')
    return redirect('/adotar')

def processa_pedido_adocao(request, id_pedido):
    status = request.GET.get('status')
    pedido = PedidoAdocao.objects.get(id=id_pedido)
    if status == "A":
        pedido.status = 'AP'
        string = '''Olá, sua adoção foi aprovada. ...'''
    elif status == "R":
        string = '''Olá, sua adoção foi recusada. ...'''
        pedido.status = 'R'

    pedido.save()

    print(pedido.usuario.email)
    
    email = send_mail(
        'Sua adoção foi processada',
        string,
        'maristela.senacdf@gmail.com',
        [pedido.usuario.email,],
    )
    
    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção processado com sucesso')
    return redirect('/divulgar/ver_pedido_adocao')



    
