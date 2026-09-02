# 🌍 Rota Küresi: Python'dan Unreal'a

OpenFlights açık veri setinden İstanbul (IST) çıkışlı uçuş rotalarını okuyan, büyük daire (Great Circle) interpolasyonu ile ara noktaları hesaplayan ve Unreal Engine 5 üzerinde 3B küre üzerinde spline eğrileriyle görselleştiren uçtan uca veri projesi.

![Rota Küresi Önizleme](docs/preview.jpg)

---

## 🚀 Proje Mimarisi

```mermaid
flowchart LR
    A["OpenFlights Verisi (airports.dat, routes.dat)"] --> B["rotalar.py (Python)"]
    B --> C["Büyük Daire İnterpolasyonu (32 Nokta)"]
    C --> D["rotalar.csv"]
    D --> E["Unreal Engine 5 (DataTable)"]
    E --> F["3B Küre & Spline Çizimi"]
```

---

## 📁 Proje Yapısı

* **`rotalar.py`**: OpenFlights verilerini indiren, İstanbul çıkışlı rotaları filtreleyen ve her rota için 32 büyük daire ara noktası hesaplayıp CSV'ye döken Python betiği.
* **`rotalar.csv`**: UE5 DataTable yapısına uygun üretilen rota veri seti (`id, hedef, sira, enlem, boylam`).
* **`UE5/`**: Unreal Engine 5 aktör yapısı, Blueprint dönüşüm matematiği ve DataTable entegrasyon kılavuzu.
* **`docs/preview.jpg`**: Proje görselleştirmesi ve önizleme ekran görüntüsü.

---

## 🛠️ Nasıl Çalıştırılır?

### 1. Python ile Rota Verisini Üretme
Terminalde tek bir komutla tüm veriyi indirip `rotalar.csv` dosyasını oluşturabilirsiniz:

```bash
python3 rotalar.py
```

* Çıktı olarak **226 tekil rota** ve toplam **7.232 ara nokta** üretilecektir.

### 2. Unreal Engine 5'te Görselleştirme
1. UE5 içerisinde `FRoutePoint` yapısını (Struct: `hedef`, `sira`, `enlem`, `boylam`) oluşturun.
2. `rotalar.csv` dosyasını `DataTable` olarak içe aktarın.
3. `BP_FlightGlobe` aktöründe enlem ve boylam değerlerini küre koordinatlarına çevirin:
   $$X = R \cdot \cos(lat) \cdot \cos(lon)$$
   $$Y = R \cdot \cos(lat) \cdot \sin(lon)$$
   $$Z = R \cdot \sin(lat)$$
4. Spline Component kullanarak noktaları birleştirin ve ince ışıltılı hatlar çizin. Detaylı adımlar için [`UE5/README.md`](UE5/README.md) kılavuzunu inceleyin.

---

## 📐 Büyük Daire (Great Circle) İnterpolasyon Formülü

İki coğrafi nokta $(lat_1, lon_1)$ ve $(lat_2, lon_2)$ arasındaki küresel mesafe ve $f \in [0, 1]$ ara noktası şu formülle hesaplanır:

$$d = 2 \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{lat_2 - lat_1}{2}\right) + \cos(lat_1) \cdot \cos(lat_2) \cdot \sin^2\left(\frac{lon_2 - lon_1}{2}\right)}\right)$$

$$A = \frac{\sin((1-f) \cdot d)}{\sin(d)}, \quad B = \frac{\sin(f \cdot d)}{\sin(d)}$$

$$x = A \cos(lat_1)\cos(lon_1) + B \cos(lat_2)\cos(lon_2)$$
$$y = A \cos(lat_1)\sin(lon_1) + B \cos(lat_2)\sin(lon_2)$$
$$z = A \sin(lat_1) + B \sin(lat_2)$$

$$lat = \text{atan2}(z, \sqrt{x^2 + y^2}), \quad lon = \text{atan2}(y, x)$$

---

## 🏆 Bonus: İstanbul'dan (IST) En Uzak 5 Uçuş Rotası

Python tarafında $d \cdot 6371\text{ km}$ formülü ile hesaplanan en uzak 5 hedef:

| Sıra | IATA | Havalimanı Adı | Ülke | Kuş Uçuşu Mesafe |
| :---: | :---: | :--- | :--- | :---: |
| **1** | **LAX** | Los Angeles International Airport | Amerika Birleşik Devletleri | **11.002,3 km** |
| **2** | **GRU** | Guarulhos - Gov. André Franco Montoro Intl. | Brezilya | **10.559,4 km** |
| **3** | **IAH** | George Bush Intercontinental Houston | Amerika Birleşik Devletleri | **10.231,9 km** |
| **4** | **NRT** | Narita International Airport | Japonya | **8.979,1 km** |
| **5** | **ORD** | Chicago O'Hare International Airport | Amerika Birleşik Devletleri | **8.785,9 km** |
