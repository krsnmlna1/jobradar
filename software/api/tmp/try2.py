from contextlib import contextmanager


@contextmanager
def pinjam_koneksi():
    print("  pinjam")
    try:
        yield "koneksi_palsu"
    finally:
        print("  balikin")


def handler_sukses():
    with pinjam_koneksi() as conn:
        print(f"  pakai {conn}")


def handler_gagal():
    with pinjam_koneksi():
        raise ValueError("404 pura-pura")


print("sukses:")
handler_sukses()

print("gagal:")
try:
    handler_gagal()
except ValueError:
    pass
