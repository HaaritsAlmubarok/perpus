from django.test import TestCase, Client
from django.urls import reverse
from .models import Siswa, Buku, Peminjaman
import datetime

class PeminjamanTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.siswa = Siswa.objects.create(
            nama="Budi",
            kelas="X-A",
            nis="12345",
            status="Aktif"
        )
        self.buku = Buku.objects.create(
            judul="Python 101",
            pengarang="Author",
            kategori="Programming",
            penerbit="Publisher",
            tahun=2020,
            rak="A1",
            stok=5,
            isbn="978-3-16-148410-0",
            deskripsi="Python book"
        )

    def test_tambah_peminjam_get(self):
        response = self.client.get(reverse('tambah_peminjam'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('siswa_list', response.context)
        self.assertIn('buku_list', response.context)
        self.assertEqual(len(response.context['siswa_list']), 1)
        self.assertEqual(len(response.context['buku_list']), 1)

    def test_tambah_peminjam_post(self):
        # Initial checks
        self.assertEqual(Peminjaman.objects.count(), 0)
        self.assertEqual(Buku.objects.get(id=self.buku.id).stok, 5)

        data = {
            'nama_peminjam': 'Budi',
            'buku': 'Python 101',
            'tanggal_pinjam': '2026-06-09',
            'jatuh_tempo': '2026-06-16',
            'keterangan': 'Tugas sekolah',
            'catatan': 'Harap kembalikan tepat waktu',
            'petugas': 'Haarits'
        }
        response = self.client.post(reverse('tambah_peminjam'), data)
        self.assertRedirects(response, reverse('list_peminjam'))

        # Check Peminjaman created
        self.assertEqual(Peminjaman.objects.count(), 1)
        p = Peminjaman.objects.first()
        self.assertEqual(p.nama_peminjam, 'Budi')
        self.assertEqual(p.buku, 'Python 101')
        self.assertEqual(p.keterangan, 'Tugas sekolah - Harap kembalikan tepat waktu')
        self.assertEqual(p.petugas, 'Haarits')
        self.assertEqual(p.status, 'Dipinjam')

        # Check stock decreased
        self.buku.refresh_from_db()
        self.assertEqual(self.buku.stok, 4)

    def test_ubah_status_peminjam(self):
        p = Peminjaman.objects.create(
            nama_peminjam='Budi',
            buku='Python 101',
            tanggal_pinjam=datetime.date(2026, 6, 9),
            jatuh_tempo=datetime.date(2026, 6, 16),
            keterangan='Test',
            petugas='Haarits',
            status='Dipinjam'
        )
        self.assertEqual(Buku.objects.get(id=self.buku.id).stok, 5)

        # Update status to Dikembalikan
        response = self.client.post(reverse('ubah_status', args=[p.id]), {'status': 'Dikembalikan'})
        self.assertRedirects(response, reverse('list_peminjam'))

        p.refresh_from_db()
        self.assertEqual(p.status, 'Dikembalikan')

        # Stock should increase to 6 (5 + 1 returned)
        self.buku.refresh_from_db()
        self.assertEqual(self.buku.stok, 6)

    def test_dashboard_view(self):
        # Create an extra book to test sum/count
        Buku.objects.create(
            judul="Django Book",
            stok=3
        )
        # Create a loan
        Peminjaman.objects.create(
            nama_peminjam='Budi',
            buku='Python 101',
            tanggal_pinjam=datetime.date(2026, 6, 9),
            jatuh_tempo=datetime.date(2026, 6, 16),
            keterangan='Test',
            petugas='Haarits',
            status='Dipinjam'
        )

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_buku'], 8) # 5 (Python 101) + 3 (Django Book)
        self.assertEqual(response.context['total_judul'], 2)
        self.assertEqual(response.context['sedang_dipinjam'], 1)
        self.assertEqual(response.context['sudah_dikembalikan'], 0)

    def test_tambah_peminjam_out_of_stock(self):
        # Set stock to 0
        self.buku.stok = 0
        self.buku.save()

        data = {
            'nama_peminjam': 'Budi',
            'buku': 'Python 101',
            'tanggal_pinjam': '2026-06-09',
            'jatuh_tempo': '2026-06-16',
            'keterangan': 'Tugas sekolah',
            'catatan': 'Harap kembalikan tepat waktu',
            'petugas': 'Haarits'
        }
        response = self.client.post(reverse('tambah_peminjam'), data)
        
        # Should not redirect, but render page with error message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Peminjaman.objects.count(), 0)
        
        # Check that the out-of-stock book is not in the dropdown context list
        self.assertEqual(len(response.context['buku_list']), 0)
