from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from .models import Siswa, Buku, Peminjaman


# ==== DASHBOARD ====

def dashboard(request):
    from django.db.models import Sum
    # Total Buku (Sum of stock of all books)
    total_buku = Buku.objects.aggregate(total=Sum('stok'))['total'] or 0
    
    # Total Judul (Number of unique books)
    total_judul = Buku.objects.count()
    
    # Sedang Dipinjam
    sedang_dipinjam = Peminjaman.objects.filter(status='Dipinjam').count()
    
    # Sudah Dikembalikan
    sudah_dikembalikan = Peminjaman.objects.filter(status='Dikembalikan').count()
    
    # Distribusi Stok Buku (progress bars)
    buku_list = Buku.objects.all().order_by('-stok')
    max_stok = max([b.stok for b in buku_list] or [10])
    max_val = max(10, max_stok)
    
    # Add calculated percentage to each book object for progress bar
    for b in buku_list:
        b.persen_stok = (b.stok / max_val) * 100
        
    # Ringkasan Transaksi
    total_peminjaman = sedang_dipinjam + sudah_dikembalikan
    persen_dipinjam = (sedang_dipinjam / total_peminjaman * 100) if total_peminjaman > 0 else 0
    persen_dikembalikan = (sudah_dikembalikan / total_peminjaman * 100) if total_peminjaman > 0 else 0
    
    return render(request, 'dashboard.html', {
        'total_buku': total_buku,
        'total_judul': total_judul,
        'sedang_dipinjam': sedang_dipinjam,
        'sudah_dikembalikan': sudah_dikembalikan,
        'buku_list': buku_list,
        'persen_dipinjam': persen_dipinjam,
        'persen_dikembalikan': persen_dikembalikan,
    })


# ==== TABLE BUKU ====

def list_buku(request):
    buku_list = Buku.objects.all().order_by('id')
    total = buku_list.count()
    return render(request, 'buku/list.html', {
        'buku_list': buku_list,
        'total': total,
    })

def tambah_buku(request):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        pengarang = request.POST.get('pengarang')
        kategori = request.POST.get('kategori')
        penerbit = request.POST.get('penerbit')
        tahun = request.POST.get('tahun')
        rak = request.POST.get('rak')
        stok = request.POST.get('stok')
        isbn = request.POST.get('isbn')
        deskripsi = request.POST.get('deskripsi')

        if judul:
            buku = Buku.objects.create(
                judul=judul,
                pengarang=pengarang or '',
                kategori=kategori or '',
                penerbit=penerbit or '',
                tahun=int(tahun) if tahun else None,
                rak=rak or '',
                stok=int(stok) if stok else 0,
                isbn=isbn or '',
                deskripsi=deskripsi or '',
            )
            messages.success(request, 'Buku berhasil ditambahkan.')
            return redirect('list_buku')

    return render(request, 'buku/tambah.html')

def detail_buku(request, id):
    buku = get_object_or_404(Buku, id=id)
    return render(request, 'buku/detail.html', {
        'buku': buku,
    })

def edit_buku(request, id):
    buku = get_object_or_404(Buku, id=id)
    if request.method == 'POST':
        buku.judul = request.POST.get('judul')
        buku.pengarang = request.POST.get('pengarang')
        buku.kategori = request.POST.get('kategori')
        buku.penerbit = request.POST.get('penerbit')
        tahun = request.POST.get('tahun')
        buku.tahun = int(tahun) if tahun else None
        buku.rak = request.POST.get('rak')
        stok = request.POST.get('stok')
        buku.stok = int(stok) if stok else 0
        buku.isbn = request.POST.get('isbn')
        buku.deskripsi = request.POST.get('deskripsi')
        buku.save()
        messages.success(request, 'Data buku berhasil diperbarui.')
        return redirect('list_buku')
    
    return render(request, 'buku/edit.html', {
        'buku': buku,
    })

def hapus_buku(request, id):
    buku = get_object_or_404(Buku, id=id)
    if request.method == 'POST':
        buku.delete()
        messages.success(request, 'Data buku berhasil dihapus.')
        return redirect('list_buku')

    return render(request, 'buku/hapus.html', {
        'buku': buku,
    })



# ==== TABLE SISWA ====

def list_siswa(request):
    siswa_list = Siswa.objects.all().order_by('id')
    return render(request, 'siswa/list.html', {
        'siswa_list': siswa_list,
    })

def tambah_siswa(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        kelas = request.POST.get('kelas')
        nis = request.POST.get('nis')
        status = request.POST.get('status')

        if nama and kelas and nis and status:
            Siswa.objects.create(
                nama=nama,
                kelas=kelas,
                nis=nis,
                status=status,
            )
            return redirect('list_siswa')

    return render(request, 'siswa/tambah.html')

def detail_siswa(request, id):
    siswa = get_object_or_404(Siswa, id=id)
    total_peminjaman = Peminjaman.objects.filter(nama_peminjam=siswa.nama).count()
    peminjaman_aktif = Peminjaman.objects.filter(
        nama_peminjam=siswa.nama,
        status='Dipinjam'
    ).count()
    return render(request, 'siswa/detail.html', {
        'siswa': siswa,
        'total_peminjaman': total_peminjaman,
        'peminjaman_aktif': peminjaman_aktif,
    })

def edit_siswa(request, id):
    siswa = get_object_or_404(Siswa, id=id)
    if request.method == 'POST':
        siswa.nama = request.POST.get('nama')
        siswa.kelas = request.POST.get('kelas')
        siswa.nis = request.POST.get('nis')
        siswa.status = request.POST.get('status')
        siswa.save()
        messages.success(request, 'Data user berhasil diperbarui.')
        return redirect('detail_siswa', id=siswa.id)

    return render(request, 'siswa/edit.html', {
        'siswa': siswa,
    })

def hapus_siswa(request, id):
    siswa = get_object_or_404(Siswa, id=id)
    if request.method == 'POST':
        siswa.delete()
        messages.success(request, 'Data siswa berhasil dihapus.')
        return redirect('list_siswa')

    return render(request, 'siswa/hapus.html', {
        'siswa': siswa,
    })



# ==== TABLE PEMINJAM ====

def list_peminjam(request):
    peminjaman_list = Peminjaman.objects.all().order_by('-id')
    return render(request, 'peminjaman/list.html', {
        'peminjaman_list': peminjaman_list,
    })

def tambah_peminjam(request):
    if request.method == 'POST':
        nama_peminjam = request.POST.get('nama_peminjam')
        buku_judul = request.POST.get('buku')
        tanggal_pinjam = request.POST.get('tanggal_pinjam')
        jatuh_tempo = request.POST.get('jatuh_tempo')
        keterangan = request.POST.get('keterangan', '')
        catatan = request.POST.get('catatan', '')
        petugas = request.POST.get('petugas')

        # Gabungkan keterangan dan catatan
        full_keterangan = keterangan
        if catatan:
            if full_keterangan:
                full_keterangan += f" - {catatan}"
            else:
                full_keterangan = catatan

        if nama_peminjam and buku_judul and tanggal_pinjam and jatuh_tempo and petugas:
            # Validasi stok buku
            buku_obj = Buku.objects.filter(judul=buku_judul).first()
            if not buku_obj or buku_obj.stok <= 0:
                messages.error(request, f'Buku "{buku_judul}" tidak tersedia atau stoknya sudah habis.')
                siswa_list = Siswa.objects.all().order_by('nama')
                buku_list = Buku.objects.filter(stok__gt=0).order_by('judul')
                return render(request, 'peminjaman/tambah.html', {
                    'siswa_list': siswa_list,
                    'buku_list': buku_list,
                })

            # Simpan peminjaman baru
            Peminjaman.objects.create(
                nama_peminjam=nama_peminjam,
                buku=buku_judul,
                tanggal_pinjam=tanggal_pinjam,
                jatuh_tempo=jatuh_tempo,
                keterangan=full_keterangan,
                petugas=petugas,
                status='Dipinjam'
            )
            
            # Kurangi stok buku
            try:
                buku_obj.stok -= 1
                buku_obj.save()
            except Exception:
                pass

            messages.success(request, 'Peminjaman berhasil ditambahkan.')
            return redirect('list_peminjam')

    siswa_list = Siswa.objects.all().order_by('nama')
    buku_list = Buku.objects.filter(stok__gt=0).order_by('judul')
    return render(request, 'peminjaman/tambah.html', {
        'siswa_list': siswa_list,
        'buku_list': buku_list,
    })

def detail_peminjam(request, id):
    peminjaman = get_object_or_404(Peminjaman, id=id)
    return render(request, 'peminjaman/detail.html', {
        'peminjaman': peminjaman,
    })

def ubah_status(request, id):
    peminjaman = get_object_or_404(Peminjaman, id=id)
    if request.method == 'POST':
        status_baru = request.POST.get('status')
        if status_baru in ['Dipinjam', 'Dikembalikan']:
            # Jika status berubah dari Dipinjam ke Dikembalikan, kita kembalikan stok buku
            if peminjaman.status == 'Dipinjam' and status_baru == 'Dikembalikan':
                try:
                    buku_obj = Buku.objects.filter(judul=peminjaman.buku).first()
                    if buku_obj:
                        buku_obj.stok += 1
                        buku_obj.save()
                except Exception:
                    pass
            # Jika status berubah dari Dikembalikan ke Dipinjam, kita kurangi stok buku
            elif peminjaman.status == 'Dikembalikan' and status_baru == 'Dipinjam':
                try:
                    buku_obj = Buku.objects.filter(judul=peminjaman.buku).first()
                    if buku_obj and buku_obj.stok > 0:
                        buku_obj.stok -= 1
                        buku_obj.save()
                except Exception:
                    pass
                    
            peminjaman.status = status_baru
            peminjaman.save()
            messages.success(request, 'Status peminjaman berhasil diperbarui.')
            return redirect('list_peminjam')
            
    return render(request, 'peminjaman/ubah_status.html', {
        'peminjaman': peminjaman,
    })
