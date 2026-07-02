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

### `/lidar/points_base_link`, `/stereo/points_base_link`
**Typ:** `sensor_msgs/PointCloud2` (4 Felder: x, y, z, weight)
**Publisher:** je eine Instanz von `frame_transform_node` (Lidar / Stereo)
**Frame:** `base_link`
Dieselben Punkte wie oben, per TF2 in das Roboter-Koordinatensystem
transformiert. `frame_transform_node` transformiert nur x/y/z — das
`weight`-Feld läuft unverändert durch (`tf2_sensor_msgs.do_transform_cloud`
lässt zusätzliche Felder unangetastet).

### `/lidar/points_filtered`, `/stereo/points_filtered`
**Typ:** `sensor_msgs/PointCloud2` (4 Felder: x, y, z, weight)
**Publisher:** je eine Instanz von `pointcloud_preprocessing_node`
**Frame:** `base_link`
Nach Crop / Voxel-Downsampling / Radius-Outlier-Removal (Parameter pro
Sensor unterschiedlich, siehe Launch-File). Falls die eingehende Cloud noch
kein `weight`-Feld hat (aktuell: der Lidar-Zweig), wird hier `weight = 1.0`
(volles Vertrauen) ergänzt.

### `/perception/global_points`
**Typ:** `sensor_msgs/PointCloud2` (4 Felder: x, y, z, weight)
**Publisher:** `global_pointcloud_fusion_node`
**Frame:** `base_link`
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
**Frame:** `base_link`
Ein Wert pro Zelle (`data`, row-major, Index `iy * width + ix`):
- `-1` = unbekannt (zu wenige Punkte in der Zelle)
- `0–60` = befahrbar, steigende "Kosten" je näher an den Grenzwerten
- `80` = nicht befahrbar (zu rau oder zu steil)
- `100` = nicht befahrbar (Stufe/Sprung zu hoch)

### `/terrain/terrain_grid_stats` (custom message)
**Typ:** `rover_perception_msgs/TerrainGrid`
**Publisher:** `obstacle_grid_node`
**Frame:** `base_link`
Dieselbe Grid-Geometrie und dasselbe `info` (Auflösung/Breite/Höhe/Ursprung)
wie `/terrain/traversability_grid` — Zellen sind 1:1 per Index vergleichbar.
Enthält zusätzlich die rohen Zellstatistiken, aus denen der obige
Traversability-Wert abgeleitet wird:

| Feld              | Typ        | Bedeutung                                                        |
|-------------------|------------|--------------------------------------------------------------------|
| `header`          | `std_msgs/Header` | Stamp + `frame_id` (`base_link`)                            |
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
