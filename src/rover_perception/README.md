# rover_perception – Message-/Topic-Referenz

Alle Nachrichten, die durch die Stereo+Lidar-Fusion-Pipeline laufen, in der
Reihenfolge, in der sie entstehen. Für die Gesamtarchitektur siehe
`ARCHITECTURE.md`.

---

### `/livox/points`
**Typ:** `sensor_msgs/PointCloud2`
**Publisher:** `rover_lidar` (`fake_lidar_node`, später `livox_ros_driver2`)
**Frame:** `lidar_frame`
Rohe Lidar-Punkte (x, y, z), unverändert vom Sensor.

### `/camera/depth/image_rect_raw`
**Typ:** `sensor_msgs/Image` (Encoding `16UC1`)
**Publisher:** `rover_perception` (`fake_stereo_camera_node`, später `realsense2_camera`)
**Frame:** `camera_depth_optical_frame`
Entzerrtes Tiefenbild, 16-bit, Werte in Millimetern, `0` = ungültiges Pixel.

### `/camera/depth/camera_info`
**Typ:** `sensor_msgs/CameraInfo`
**Publisher:** wie oben
Kamera-Intrinsics (fx, fy, cx, cy) passend zum obigen Tiefenbild — wird zur
Rückprojektion in 3D gebraucht.

### `/stereo/points`
**Typ:** `sensor_msgs/PointCloud2` (4 Felder: x, y, z, **weight**)
**Publisher:** `stereo_pointcloud_node`
**Frame:** `camera_depth_optical_frame`
Tiefenbild + CameraInfo per Pinhole-Rückprojektion in 3D-Punkte umgerechnet.
Jeder Punkt bekommt zusätzlich ein `weight`-Feld (0–1), siehe
"Gewichtungssystem" unten.

### `/lidar/points_mast_base_link`, `/stereo/points_mast_base_link`
**Typ:** `sensor_msgs/PointCloud2` (4 Felder: x, y, z, weight)
**Publisher:** je eine Instanz von `frame_transform_node` (Lidar / Stereo)
**Frame:** `mast_base_link`
Dieselben Punkte wie oben, per TF2 in das feste Referenzsystem des
Mast-Moduls transformiert (das Modul selbst bewegt sich nicht — der Rover,
der beobachtet wird, ist ein separates, bewegliches Ding, siehe Mono-Cam-
Zweig unten). `frame_transform_node` transformiert nur x/y/z — das
`weight`-Feld läuft unverändert durch (`tf2_sensor_msgs.do_transform_cloud`
lässt zusätzliche Felder unangetastet).

### `/lidar/points_filtered`, `/stereo/points_filtered`
**Typ:** `sensor_msgs/PointCloud2` (4 Felder: x, y, z, weight)
**Publisher:** je eine Instanz von `pointcloud_preprocessing_node`
**Frame:** `mast_base_link`
Nach Crop / Voxel-Downsampling / Radius-Outlier-Removal (Parameter pro
Sensor unterschiedlich, siehe Launch-File). Falls die eingehende Cloud noch
kein `weight`-Feld hat (aktuell: der Lidar-Zweig), wird hier `weight = 1.0`
(volles Vertrauen) ergänzt.

### `/perception/global_points`
**Typ:** `sensor_msgs/PointCloud2` (4 Felder: x, y, z, weight)
**Publisher:** `global_pointcloud_fusion_node`
**Frame:** `mast_base_link`
Zeitlich synchronisierte Vereinigung von gefilterter Lidar- und
Stereo-Punktwolke.

---

### Gewichtungssystem (`weight`-Feld)

Stereo-Tiefe wird bei wenig Licht und größerer Entfernung unzuverlässiger;
Lidar ist davon kaum betroffen. Statt Stereo-Punkte hart zu verwerfen, trägt
jeder Punkt ab `stereo_pointcloud_node` ein `weight`-Feld (0–1) mit, das die
ganze Pipeline durchläuft und erst in `terrain_analysis.py` ausgewertet wird:

- **Stereo:** `weight = distance_weight(z) * scene_confidence`
  - `distance_weight(z) = 1 / (1 + (z / distance_weight_ref_m)²)`, hart auf
    0 gesetzt jenseits von `max_reliable_range_m`.
  - `scene_confidence` ist ein globaler (0–1) Wert, empfangen auf
    `/camera/scene_confidence` (`std_msgs/Float32`). Es publiziert aktuell
    noch niemand dorthin — Default bleibt `1.0` (keine Abwertung), bis ein
    zukünftiger Helligkeits-/Low-Light-Node das übernimmt. Die Verkabelung
    ist real und schon jetzt testbar (`ros2 topic pub` auf diesen Topic).
- **Lidar:** hat kein natives Konfidenzmodell, bekommt `weight = 1.0`
  (siehe oben, ergänzt in `pointcloud_preprocessing_node`).
- **Aggregation** (`pointcloud_filters.py`, `terrain_analysis.py`):
  Voxel-Downsampling nutzt den gewichteten Mittelwert der Position, die
  Ebenenanpassung pro Zelle ist eine gewichtete Kleinste-Quadrate-Schätzung,
  und die Zellen-Gültigkeit (`min_points_per_cell`) wird gegen die Summe der
  Gewichte (`total_weight`) statt gegen die rohe Punktanzahl geprüft — eine
  Zelle aus vielen unsicheren (fernen/dunklen) Stereo-Punkten braucht also
  mehr "effektive" Punkte, um als bekanntes Terrain zu gelten, als eine
  Zelle mit wenigen sicheren Lidar-Rückgaben.

### `/terrain/traversability_grid`
**Typ:** `nav_msgs/OccupancyGrid`
**Publisher:** `obstacle_grid_node`
**Frame:** `mast_base_link`
Ein Wert pro Zelle (`data`, row-major, Index `iy * width + ix`):
- `-1` = unbekannt (zu wenige Punkte in der Zelle)
- `0–60` = befahrbar, steigende "Kosten" je näher an den Grenzwerten
- `80` = nicht befahrbar (zu rau oder zu steil)
- `100` = nicht befahrbar (Stufe/Sprung zu hoch)

**Persistenter Punkte-Puffer pro Zelle:** `obstacle_grid_node` berechnet das
Grid nicht mehr allein aus der zuletzt empfangenen `/perception/global_points`-
Message, sondern hält pro Zelle einen `collections.deque(maxlen=
max_points_per_cell)`-Puffer (`self.cell_buffers`, Default 50 Punkte/Zelle).
Jede neue Punktwolke wird einsortiert, alte Punkte fallen erst raus, sobald
eine Zelle voll ist (kontinuierlich gleitendes Fenster, kein harter Reset).
`build_elevation_grid()` läuft danach über den gesamten Puffer, nicht nur
über die neueste Message — so baut sich über mehrere Callbacks/Pan-Positionen
ein vollständiges Bild auf, statt bei jedem Callback bei null anzufangen.

### `/camera/imu`
**Typ:** `sensor_msgs/Imu`
**Publisher:** `fake_stereo_camera_node` (später `realsense2_camera`)
**Frame:** `camera_depth_optical_frame`
Eingebaute IMU der Stereo-Cam. Fake-Version publiziert Identity-Orientierung
(Kamera als eben/level angenommen) mit gültiger `orientation_covariance`.
Wird von `mast_pose_node` für den Plattform-IMU-Plausibilitätscheck genutzt.

### `/livox/imu`
**Typ:** `sensor_msgs/Imu`
**Publisher:** `rover_lidar` (`fake_lidar_node`, später `livox_ros_driver2`)
**Frame:** `lidar_frame`
Eingebaute IMU des Lidars. Gleiche Rolle wie `/camera/imu` oben, für den
Plausibilitätscheck in `mast_pose_node`.

### `/hardware_box/imu`
**Typ:** `sensor_msgs/Imu`
**Publisher:** `fake_mast_hw_node` (echte Hardware/Treiber existiert noch nicht)
**Frame:** `hardware_box_link`
IMU in der Elektronik-Box weiter unten am Mast — bestimmt die Neigung des
Mastes selbst (nicht der Plattform). Fließt in `mast_pose_node`s
`world -> mast_base_link`-Transform ein (nur Rotation, keine Position).

### `/mast/joint_states`
**Typ:** `sensor_msgs/JointState`
**Publisher:** `fake_mast_hw_node` (echte Motor-Controller-Schnittstelle existiert noch nicht)
Aktuelle Pan-/Tilt-Winkel (`mast_pan_joint`, `platform_tilt_joint`, Radiant).
Primäre (autoritative) Quelle für `mast_pose_node`s
`mast_base_link -> mast_platform_link`-Transform.

### `/mono_cam/image_raw`
**Typ:** `sensor_msgs/Image` (Encoding `rgb8`)
**Publisher:** `fake_mono_camera_node` (später `v4l2_camera_node`)
**Frame:** `mono_cam_optical_frame`
Farbbild der Mono-Cam, die (wie Lidar/Stereo) fest auf dem Mast montiert
ist und den beweglichen Rover von außen beobachtet — nicht Teil des Rovers
selbst. Fake-Version simuliert 3 starre LED-Panels auf dem Rover (Dach/
links/rechts, je eine eigene Farbe: grün/rot/blau), jedes mit derselben
asymmetrischen Form (gleichschenkliges Dreieck + 1 LED auf einem Schenkel
— siehe ARCHITECTURE.md). Pro Frame ist nur sichtbar, was gerade zur Kamera
zeigt (einfacher Verdeckungstest per Panel-Normale), damit sich der Rover
mit variierender Distanz, seitlicher Position und Rotation vor der Kamera
bewegen kann, ohne dass alle 3 Panels gleichzeitig "durchscheinen".

### `/mono_cam/camera_info`
**Typ:** `sensor_msgs/CameraInfo`
**Publisher:** wie oben
Intrinsics (fx, fy, cx, cy), aus dem FOV des Arducam-B0497-Datenblatts
abgeleitet — für die Rückprojektion in Sichtstrahlen in `led_detector_node`.

### `/mono_cam/led_detections` (custom message)
**Typ:** `rover_perception_msgs/LedDetectionArray`
**Publisher:** `led_detector_node`
**Frame:** `mono_cam_optical_frame`
Liste erkannter LED-Blobs pro Frame (leer = normal, kein Fehler). Ein Blob
muss drei Filter passieren: Helligkeit (`brightness_threshold`), Größe
(`min/max_blob_area_px`) und Farbe (`min_color_dominance` — der jeweils
stärkste Farbkanal muss die beiden anderen deutlich übersteigen; passt zu
allen 3 Panel-Farben grün/rot/blau gleichermaßen, da hier nur "wie eindeutig
ist die Farbe" geprüft wird, nicht gegen eine feste Ziel-Farbe; per
`enable_color_filter` abschaltbar). *Welchem* Panel ein Blob zugehört,
entscheidet dieser Node nicht — das übernimmt `position_rover_node` anhand
von `color_r/g/b`. Pro Blob (`LedDetection`):
Pixel-Zentroid (`pixel_u`/`pixel_v`), Blob-Größe (`area_px`), mittlere
Farbe (`color_r/g/b`) und ein normierter Sichtstrahl (`bearing`,
`geometry_msgs/Vector3`) im Kamera-Optical-Frame — eine Mono-Cam liefert
nur eine *Richtung*, keine Distanz; die eigentliche Positionsschätzung ist
Aufgabe von `position_rover_node`.

### `/rover/estimated_pose`
**Typ:** `geometry_msgs/PoseStamped`
**Publisher:** `position_rover_node`
**Frame:** `world`
Geschätzte Position + Orientierung des Rovers. `position_rover_node`
gruppiert die `/mono_cam/led_detections`-Blobs zunächst nach Farbe (Panel-
Zugehörigkeit: Dach=grün, links=rot, rechts=blau), löst für jedes Panel mit
genau 4 zugehörigen Blobs unabhängig ein PnP-Problem gegen die bekannte
Panel-Geometrie (gleichschenkliges Dreieck + 1 Schenkel-LED), verrechnet die
beste Panel-Lösung mit der festen Panel->Rover-Mittelpunkt-Montage-
Transformation zu einer Rover-Pose, und rechnet diese über den TF-Baum
(`world -> mast_base_link -> mast_platform_link -> mono_cam_optical_frame`)
in den `world`-Frame um. Wird bei zu unsicherem Fit (`max_fit_residual_deg`)
oder zu wenigen erkannten LEDs (`min_detections`) für diesen Frame
übersprungen, statt einen schlechten Wert zu publizieren. Zusätzlich wird
derselbe Pose-Schätzwert als TF (`world -> rover_estimated_link`) gebroadcastet,
zur einfachen Visualisierung in RViz2.

Da die Panel-Form (Dreieck + Schenkel-LED) keinerlei Rotations- oder
Spiegelsymmetrie hat, ist die Ecken-Zuordnung pro Panel eindeutig (alle 24
Permutationen werden geprüft, siehe ARCHITECTURE.md) — anders als beim
früheren symmetrischen 5-LED-"Würfel"-Muster gibt es hier **keine**
Yaw-Mehrdeutigkeit mehr: eine gute Passung legt die volle Orientierung fest.

### `/terrain/terrain_grid_stats` (custom message)
**Typ:** `rover_perception_msgs/TerrainGrid`
**Publisher:** `obstacle_grid_node`
**Frame:** `mast_base_link`
Dieselbe Grid-Geometrie und dasselbe `info` (Auflösung/Breite/Höhe/Ursprung)
wie `/terrain/traversability_grid` — Zellen sind 1:1 per Index vergleichbar.
Enthält zusätzlich die rohen Zellstatistiken, aus denen der obige
Traversability-Wert abgeleitet wird:

| Feld              | Typ        | Bedeutung                                                        |
|-------------------|------------|--------------------------------------------------------------------|
| `header`          | `std_msgs/Header` | Stamp + `frame_id` (`mast_base_link`)                       |
| `info`            | `nav_msgs/MapMetaData` | Auflösung, Breite, Höhe, Ursprungspose des Grids        |
| `traversability`  | `int8[]`   | identisch zu `OccupancyGrid.data` (s.o.), zur einfachen Korrelation |
| `min_z`           | `float32[]`| niedrigster Punkt in der Zelle (m)                                  |
| `max_z`           | `float32[]`| höchster Punkt in der Zelle (m)                                     |
| `mean_z`          | `float32[]`| mittlere Höhe der Zelle (m)                                         |
| `roughness`       | `float32[]`| Standardabweichung der Residuen zur gefitteten Ebene (m)            |
| `plane_slope_deg` | `float32[]`| Neigung der gefitteten Ebene in der Zelle (Grad)                    |
| `point_count`     | `int32[]`  | rohe Anzahl der Punkte, die in die Zelle gefallen sind (Diagnose)   |
| `total_weight`    | `float32[]`| Summe der Punkt-Gewichte in der Zelle — **das** entscheidet (nicht `point_count`), ob die Zelle als bekanntes Terrain gilt |

Zellen ohne genug effektive Punkte (`total_weight < min_points_per_cell`):
alle `float32`-Felder = `NaN`, `point_count`/`total_weight` = 0 (bewusst
kein gemeinsamer Sentinel-Wert wie bei der OccupancyGrid, da das
kontinuierliche Größen sind statt eines begrenzten 0–100-Kostenwerts).

### `/terrain/elevation_cloud`
**Typ:** `sensor_msgs/PointCloud2` (Felder: x, y, z, intensity)
**Publisher:** `terrain_visualization_node`
**Frame:** `mast_base_link`
Für RViz2 gedacht: wandelt `/terrain/terrain_grid_stats` in eine Standard-
PointCloud2 um, da RViz das custom `TerrainGrid` nicht kennt. Ein Punkt pro
gültiger Zelle (NaN-Zellen werden übersprungen): `x`/`y` = Zellenmittelpunkt,
`z` = echte Höhe (`mean_z`, nicht normiert), `intensity` = per Parameter
`color_field` wählbar (Default `mean_z`, auch möglich: `roughness`,
`plane_slope_deg`, `traversability`). In RViz: PointCloud2-Display,
Color Transformer "Intensity", Style "Squares"/"Boxes" mit Size ≈
`grid_resolution` für einen flächigen Zell-Look.
