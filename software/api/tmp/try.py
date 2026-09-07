import asyncio
import time


async def pelayan(nomor):
    print(f"meja {nomor}: pesan")
    await asyncio.sleep(2)  # ← coba ganti time.sleep(2)
    print(f"meja {nomor}: dianter")


async def main():
    mulai = time.time()
    await pelayan(1)
    await pelayan(2)
    await pelayan(3)

    print(f"total {time.time() - mulai:.1f} detik")


asyncio.run(main())
