from django.db import models


class Proyecto(models.Model):
    slug = models.SlugField(unique=True)
    titulo = models.CharField(max_length=200)
    acronimo = models.CharField(max_length=50, blank=True)
    resumen = models.TextField(blank=True)
    cuerpo = models.TextField(blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    url_oficial = models.URLField(blank=True)

    def __str__(self):
        return self.titulo


class Entrada(models.Model):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="entradas"
    )
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    fecha_publicacion = models.DateField(auto_now_add=True)
    resumen = models.TextField(blank=True)
    cuerpo = models.TextField()
    imagen_destacada = models.ImageField(
        upload_to="entradas/portadas/%Y/%m/%d", blank=True, null=True
    )
    url_original = models.URLField(blank=True, help_text="URL original de la noticia en el sitio madmusic.iccmu.es")

    class Meta:
        ordering = ["-fecha_publicacion"]

    def __str__(self):
        return self.titulo


class Pagina(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paginas",
    )
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    cuerpo = models.TextField()

    def __str__(self):
        return self.titulo
