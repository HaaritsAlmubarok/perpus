from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # BUKU
    path('buku/', views.list_buku, name='list_buku'),
    path('buku/tambah/', views.tambah_buku, name='tambah_buku'),
    path('buku/<int:id>/', views.detail_buku, name='detail_buku'),
    path('buku/<int:id>/edit/', views.edit_buku, name='edit_buku'),
    path('buku/<int:id>/hapus/', views.hapus_buku, name='hapus_buku'),

    # SISWA
    path('siswa/', views.list_siswa, name='list_siswa'),
    path('siswa/tambah/', views.tambah_siswa, name='tambah_siswa'),
    path('siswa/<int:id>/', views.detail_siswa, name='detail_siswa'),
    path('siswa/<int:id>/edit/', views.edit_siswa, name='edit_siswa'),
    path('siswa/<int:id>/hapus/', views.hapus_siswa, name='hapus_siswa'),

    # PEMINJAMAN
    path('peminjaman/', views.list_peminjam, name='list_peminjam'),
    path('peminjaman/tambah/', views.tambah_peminjam, name='tambah_peminjam'),
    path('peminjaman/<int:id>/', views.detail_peminjam, name='detail_peminjam'),
    path('peminjaman/<int:id>/status/', views.ubah_status, name='ubah_status'),
]