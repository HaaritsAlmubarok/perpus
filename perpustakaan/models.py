from django.db import models

# Create your models here.

class Siswa(models.Model):
    nama = models.CharField(max_length=150)
    kelas = models.CharField(max_length=50)
    nis = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.nama


class Buku(models.Model):
    judul = models.CharField(max_length=255)
    pengarang = models.CharField(max_length=150, blank=True)
    kategori = models.CharField(max_length=100, blank=True)
    penerbit = models.CharField(max_length=150, blank=True)
    tahun = models.PositiveIntegerField(null=True, blank=True)
    rak = models.CharField(max_length=50, blank=True)
    stok = models.PositiveIntegerField(default=0)
    isbn = models.CharField(max_length=20, blank=True)
    deskripsi = models.TextField(blank=True)

    def __str__(self):
        return self.judul


class Peminjaman(models.Model):
    nama_peminjam = models.CharField(max_length=150)
    buku = models.CharField(max_length=255)
    tanggal_pinjam = models.DateField()
    jatuh_tempo = models.DateField()
    keterangan = models.TextField(blank=True)
    petugas = models.CharField(max_length=150)
    status = models.CharField(max_length=30, default='Dipinjam')

    def __str__(self):
        return f"{self.nama_peminjam} - {self.buku}"
