from django.shortcuts import render, redirect
from .models import Tarea 

# Create your views here.

def gestionar_tareas (request):
    if request.method == 'POST':
        nuevo_titulo = request.POST.get('titulo_tarea')

        if nuevo_titulo:
            nueva_tarea = Tarea(titulo=nuevo_titulo)
            nueva_tarea.save()

        return redirect('inicio')


    todas_las_tareas = Tarea.objects
   
    contexto = {
        'tareas': todas_las_tareas
    }

    return render(request, 'inicio/index.html', contexto)



def completar_tarea(request, tarea_id):
    tarea = Tarea.object(id=tarea_id).first()

    if tarea:
        tarea.completada = not tarea.completada
        tarea.save()

    return redirect('inicio')


def eliminar_tarea(request, tarea_id):
    tarea = Tarea.object(id=tarea_id).first()

    if tarea:
        tarea.delete()

    return redirect('inicio')

    
    
