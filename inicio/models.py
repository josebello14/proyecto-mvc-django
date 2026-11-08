from mongoengine import Document, StringField, BooleanField 

# Create your models here.

class Tarea(Document):
    titulo = StringField(max_length=100, required=True)
    descipcion = StringField(blank=True)
    completada = BooleanField(default=False)

    def str(self):
        return self.titulo