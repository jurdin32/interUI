import datetime


class Persona:
    def __init__(self, nombre: str, apellido: str, estado_civil: str, edad: int, anio_nacimiento: int, sexo: str):
        self.nombre = nombre
        self.apellido = apellido
        self.estado_civil = estado_civil
        self.edad = edad
        self.anio_nacimiento = anio_nacimiento
        self.sexo = sexo

    def getPersona(self):
        dict_datos = {
            "Nombre": self.nombre,
            "Apellido": self.apellido,
            "Estado Civil": self.estado_civil,
            "Edad": self.calcularEdad(),
            "Año de Nacimiento": self.anio_nacimiento,
            "Sexo": self.sexo
        }
        return dict_datos
    
    def calcularEdad(self):
        anio_actual = datetime.datetime.now().year
        edad = anio_actual - self.anio_nacimiento
        return edad
