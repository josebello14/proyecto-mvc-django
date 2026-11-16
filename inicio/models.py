from mongoengine import Document, StringField, BooleanField, IntField

# Create your models here.

class Tarea(Document):
    titulo = StringField(max_length=100, required=True)
    descipcion = StringField(blank=True)
    completada = BooleanField(default=False)

    def str(self):
        return self.titulo

# Modelo para la vista del catalogo
class Autos(Document):
    nombre = StringField(max_length=100, required=True)
    precio = IntField(blank=True)
    imagen = StringField(blank=True)

    def __str__(self):
        return self.nombre