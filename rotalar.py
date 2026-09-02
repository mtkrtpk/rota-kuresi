#!/usr/bin/env python3
"""
Rota Küresi - rotalar.py
OpenFlights verisinden İstanbul (IST) çıkışlı uçuş rotalarını okur,
büyük daire formülü ile 32 ara nokta hesaplar ve rotalar.csv dosyasına yazar.
"""

import os
import csv
import math
import subprocess

AIRPORTS_FILE = "airports.dat"
ROUTES_FILE = "routes.dat"
OUTPUT_CSV = "rotalar.csv"
SOURCE_IATA = "IST"
NUM_WAYPOINTS = 32
EARTH_RADIUS_KM = 6371.0


def download_file_if_missing(filename: str, url: str):
    """Dosya mevcut değilse curl ile indirir."""
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        print(f"📥 {filename} indiriliyor...")
        cmd = ["curl", "-sSL", url, "-o", filename]
        res = subprocess.run(cmd)
        if res.returncode != 0 or not os.path.exists(filename):
            raise RuntimeError(f"{filename} indirilemedi! URL: {url}")
        print(f"✅ {filename} indirildi ({os.path.getsize(filename) / 1024:.1f} KB).")


def load_airports(filepath: str) -> dict:
    """
    airports.dat dosyasından IATA -> (enlem, boylam, isim, ulke) sözlüğü oluşturur.
    Format: ID, Name, City, Country, IATA, ICAO, Lat, Lon, ...
    """
    airports = {}
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 7:
                iata = row[4].strip()
                name = row[1].strip()
                country = row[3].strip()
                try:
                    lat = float(row[6].strip())
                    lon = float(row[7].strip())
                    if iata and iata != r"\N":
                        airports[iata] = {
                            "lat": lat,
                            "lon": lon,
                            "name": name,
                            "country": country,
                        }
                except ValueError:
                    continue
    return airports


def calculate_great_circle_points(lat1_deg: float, lon1_deg: float,
                                  lat2_deg: float, lon2_deg: float,
                                  num_points: int = 32):
    """
    İki enlem/boylam noktası arasında büyük daire ara noktalarını hesaplar.
    Açısal mesafe d (radyan) ve 0..1 arası f parametresi ile interpolasyon yapar.
    """
    lat1 = math.radians(lat1_deg)
    lon1 = math.radians(lon1_deg)
    lat2 = math.radians(lat2_deg)
    lon2 = math.radians(lon2_deg)

    # Açısal mesafe d formülü
    d = 2 * math.asin(
        math.sqrt(
            math.sin((lat2 - lat1) / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
        )
    )

    # Eğer kaynak ve hedef aynıysa
    if d == 0:
        return [(lat1_deg, lon1_deg)] * num_points, 0.0

    points = []
    for i in range(num_points):
        f = i / (num_points - 1)
        A = math.sin((1 - f) * d) / math.sin(d)
        B = math.sin(f * d) / math.sin(d)

        x = A * math.cos(lat1) * math.cos(lon1) + B * math.cos(lat2) * math.cos(lon2)
        y = A * math.cos(lat1) * math.sin(lon1) + B * math.cos(lat2) * math.sin(lon2)
        z = A * math.sin(lat1) + B * math.sin(lat2)

        lat = math.atan2(z, math.sqrt(x**2 + y**2))
        lon = math.atan2(y, x)

        points.append((math.degrees(lat), math.degrees(lon)))

    return points, d


def main():
    print("==================================================")
    print("🌍 Rota Küresi - Uçuş Verisi İşleme (rotalar.py)")
    print("==================================================")

    # 1. Gerekli açık verileri temin et
    download_file_if_missing(
        AIRPORTS_FILE,
        "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat",
    )
    download_file_if_missing(
        ROUTES_FILE,
        "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat",
    )

    # 2. Havalimanı sözlüğünü oluştur
    airports = load_airports(AIRPORTS_FILE)
    print(f"📍 Toplam {len(airports)} havalimanı koordinatı yüklendi.")

    if SOURCE_IATA not in airports:
        raise ValueError(f"Kaynak havalimanı '{SOURCE_IATA}' airports.dat içinde bulunamadı!")

    ist = airports[SOURCE_IATA]
    print(f"✈️  Kaynak: {SOURCE_IATA} ({ist['name']}, {ist['country']}) -> Enlem: {ist['lat']:.4f}, Boylam: {ist['lon']:.4f}")

    # 3. routes.dat dosyasından IST çıkışlı rotaları süz
    unique_destinations = set()
    total_route_rows = 0

    with open(ROUTES_FILE, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 4:
                src = row[2].strip()
                dst = row[4].strip()
                if src == SOURCE_IATA:
                    total_route_rows += 1
                    if dst in airports:
                        unique_destinations.add(dst)

    print(f"📊 routes.dat içinde {SOURCE_IATA} kaynaklı {total_route_rows} uçuş satırı bulundu.")
    print(f"🎯 Koordinatı bilinen tekil hedef sayısı: {len(unique_destinations)} rota.")

    # 4. Rotaları hesapla ve CSV'ye yaz
    route_distances = []
    total_points_written = 0

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # UE5 DataTable uyumlu başlık (1. sütun RowKey id, diğerleri Struct property'leri)
        writer.writerow(["id", "hedef", "sira", "enlem", "boylam"])

        row_id = 1
        for dst_iata in sorted(unique_destinations):
            dst = airports[dst_iata]
            points, d_rad = calculate_great_circle_points(
                ist["lat"], ist["lon"],
                dst["lat"], dst["lon"],
                NUM_WAYPOINTS
            )
            dist_km = d_rad * EARTH_RADIUS_KM
            route_distances.append({
                "iata": dst_iata,
                "name": dst["name"],
                "country": dst["country"],
                "distance_km": dist_km
            })

            for idx, (lat, lon) in enumerate(points):
                writer.writerow([row_id, dst_iata, idx, f"{lat:.6f}", f"{lon:.6f}"])
                row_id += 1
                total_points_written += 1

    print(f"💾 '{OUTPUT_CSV}' başarıyla oluşturuldu! (Toplam {total_points_written} satır nokta).")

    # 5. Bonus: En uzak 5 hedefi listele
    route_distances.sort(key=lambda x: x["distance_km"], reverse=True)
    print("\n🏆 İstanbul'dan (IST) En Uzak 5 Uçuş Rotası (Bonus):")
    for rank, r in enumerate(route_distances[:5], 1):
        print(f"  {rank}. {r['iata']} - {r['name']} ({r['country']}): {r['distance_km']:.1f} km")

    print("\n✅ İşlem tamamlandı. CSV dosyası hazır!")


if __name__ == "__main__":
    main()
