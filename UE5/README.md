# Unreal Engine 5 - Rota Küresi Görselleştirme Rehberi

Bu klasör, `rotalar.csv` dosyasındaki uçuş verisini Unreal Engine 5 içerisinde 3B bir küre üzerinde spline eğrileriyle çizdirmek için gereken adımları içerir.

---

## 1. DataTable Struct (Yapı) Oluşturma
1. Content Browser içinde sağ tık -> **Blueprints** -> **Structure** seç.
2. İsmini **`FRoutePoint`** yap.
3. İçine şu 4 değişkeni ekle:
   - **`hedef`** (Type: `String` veya `Name`)
   - **`sira`** (Type: `Integer`)
   - **`enlem`** (Type: `Double` / `Float`)
   - **`boylam`** (Type: `Double` / `Float`)
4. Kaydet ve kapat.

---

## 2. CSV Dosyasını DataTable Olarak İçe Aktarma
1. `rotalar-kuresi/rotalar.csv` dosyasını UE5 Content Browser içine sürükle-bırak.
2. Çıkan pencerede **DataTable Options** -> **Choose DataTable Row Type**: **`FRoutePoint`** seç.
3. **Apply** de. Artık **`DT_FlightRoutes`** isimli DataTable hazır!

---

## 3. Blueprint Actor Oluşturma (`BP_FlightGlobe`)
1. Content Browser -> Sağ tık -> **Blueprint Class** -> **Actor** seç. İsmini **`BP_FlightGlobe`** koy.
2. Bileşenler (Components):
   - **Sphere** (Static Mesh: Sphere, Scale örn: `(X=5, Y=5, Z=5)`, Yarıçap $R = 250$ cm)
   - Koyu renkli veya dünya dokulu bir materyal ata.

### 4. Blueprint Fonksiyonu: Enlem/Boylam -> 3B Vektör Dönüşümü
**Fonksiyon Adı:** `LatLonToSphereLocation`
* **Girdiler:** `Latitude (Float)`, `Longitude (Float)`, `Radius (Float)`
* **Çıktı:** `Location (Vector)`
* **Matematik:**
  - `lat_rad = DegreesToRadians(Latitude)`
  - `lon_rad = DegreesToRadians(Longitude)`
  - $X = Radius \times \cos(lat\_rad) \times \cos(lon\_rad)$
  - $Y = Radius \times \cos(lat\_rad) \times \sin(lon\_rad)$
  - $Z = Radius \times \sin(lat\_rad)$
  - `Make Vector(X, Y, Z)` döndür.

---

## 5. Rotaları Çizdirme (Event BeginPlay veya Construction Script)
1. **`Get DataTable Rows`** (`DT_FlightRoutes`) düğümünü çağır.
2. Satırları `hedef` bazında grupla veya sıralı şekilde oku:
3. Her yeni `hedef` başladığında:
   - Bir **`Add Spline Component`** oluştur.
   - 32 ara noktanın her biri için:
     - `LatLonToSphereLocation` ile 3B konumu hesapla.
     - `Add Spline Point at Position` ile Spline'a ekle.
   - İnce çizgi efekti için Spline Point'lerin arasına **Spline Mesh Component** (veya Ribbon/Niagara/Emissive Material) ata.
4. **İstanbul İşaretçisi:**
   - İstanbul koordinatı: `Lat: 41.2753, Lon: 28.7519`
   - Bu konuma küçük kırmızı/parlak bir `StaticMeshSphere` (Pin) ekle.
