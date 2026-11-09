from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Tarea 

# Create your views here.

def gestionar_tareas (request):
    if request.method == 'POST':
        nuevo_titulo = request.POST.get('titulo_tarea')

        if nuevo_titulo:
            try:
                nueva_tarea = Tarea(titulo=nuevo_titulo)
                nueva_tarea.save()
                messages.success(request, 'Tarea creada con exito!')
            except Exception as e: 
                messages.success(request, f'Ocurrio un error al guardar {str(e)}')
        else:
            messages.warning(request, 'El titulo de la tarea no puede etar vacio.')
        return redirect('inicio')


    try:
        todas_las_tareas = Tarea.objects
    except Exception as e:
        todas_las_tareas = []
        messages.error(request, 'Error critico: No se pudo conectar a MongoDB')

    contexto = {
        'tareas': todas_las_tareas
    }

    return render(request, 'inicio/index.html', contexto)



def completar_tarea(request, tarea_id):
    try:
        tarea = Tarea.object(id=tarea_id).first()
        if tarea:
            tarea.completada = not tarea.completada
            tarea.save()
            messages.success(request, 'Estado de la tarea actualizado')
    except Exception:
        messages.error(request, 'No se puedo actualizar la tarea')

    return redirect('inicio')


def eliminar_tarea(request, tarea_id):
    try:
        tarea = Tarea.object(id=tarea_id).first()
        if tarea:
            tarea.delete()
            messages.success(request, 'Tarea eliminada para siempre')
    except Exception:
        messages.error(request, 'Hubo un error al intetar eliminar la tarea')

    return redirect('inicio')

    
    
