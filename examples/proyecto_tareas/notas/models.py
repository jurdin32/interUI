"""Modelos de la app notas.

`python iui.py makemigrations` compara este archivo con la última migración y
`python iui.py migrate` aplica los cambios a la base de datos.
"""

import interui as ui


class Nota(ui.Model):
    titulo = ui.Str(max_length=120)
    hecha = ui.Bool(default=False)
    creada = ui.DateTime(auto_now_add=True)

    class Meta:
        table = "notas"
        order = ["-creada"]
