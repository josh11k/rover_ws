# rover_perception – Architektur

Für eine vollständige Liste aller Topics/Messages (inkl. Feldbeschreibung
der custom `TerrainGrid`-Message) siehe `README.md`.

Phase 1 ("Stereo+Lidar Fusion zuerst"). IMU-Fusion und die Comms-Kette aus
dem ursprünglichen Diagramm sind bewusst noch nicht implementiert (siehe
"Offene Punkte" unten). Der Mono-Cam/LED-Zweig ist im Aufbau (siehe
"Mono-Cam/LED-Zweig" unten).

## Wichtig: Mast, nicht Rover

Das komplette Perception-Modul (dieser Jetson, mit Lidar+Stereo+Mono+IMU)
sitzt auf einem ca. 120cm hohen Mast — es bewegt sich nicht mit dem Rover
mit. Der eigentliche Rover ist ein separates, bewegliches Objekt, das von
diesem Modul von außen beobachtet wird (über die Mono-Cam/LED-Erkennung).
Deshalb:

- `mast_base_link`/`mast_platform_link` sind die Referenzsysteme des
  Moduls selbst, **kein** Rover-Körper-Frame.
- Das Terrain-Traversability-Grid (`obstacle_grid_node`) ist entsprechend
  eine Karte um den Mast, keine mitfahrende Rover-lokale Karte.
- Der eigentliche Rover (eigenes `rover_control`-Package) ist ein
  unabhängiges System, dem dieses Modul die per LED-Erkennung bestimmte
  Position zuliefern soll (vermutlich per WLAN) — das schließt den Kreis
  zu `rover_pose_node` in `rover_control`, der aktuell nur einen
  hartcodierten Fake-String publiziert.

### Pan/Tilt-Kinematik (implementiert)

Der Mast ist nicht starr — er kann sich drehen (Pan, an der Basis) und
trägt an der Spitze eine kippbare Plattform (Tilt), auf der Lidar/Stereo/
Mono fest montiert sind. Eine dritte IMU sitzt in der Hardware-Box weiter
unten am Mast (Mast-Neigung, nicht Plattform). TF-Baum:

```
world --[Neigung, aus Hardware-Box-IMU]--> mast_base_link
  --[Pan+Tilt, aus Motor-Position]--> mast_platform_link
  --[fest, vermessen]--> lidar_frame / camera_depth_optical_frame /
  mono_cam_optical_frame
```

`mast_pose_node` published die zwei dynamischen Transforms (`world →
mast_base_link`, `mast_base_link → mast_platform_link`) per normalem
`tf2_ros.TransformBroadcaster` — kein Custom-Message-Umweg, `frame_transform_
node` konsumiert das automatisch über `lookup_transform`, ohne selbst
geändert zu werden. Details/Design-Entscheidungen (warum Pan nicht per IMU
korrigierbar ist, warum die Encoder-Position gegenüber der IMU als
autoritativ behandelt wird, wie die beiden Plattform-IMUs sich gegenseitig
auf Plausibilität prüfen) stehen ausführlich im Docstring von
`mast_pose_node.py`.

Fake-Gegenstücke zum Testen ohne Hardware: `fake_mast_hw_node`
(Hardware-Box-IMU + Pan/Tilt-JointState-Platzhalter, `/mast/joint_states`
und `/hardware_box/imu`), sowie IMU-Publishing direkt in
`fake_stereo_camera_node` (`/camera/imu`) und `fake_lidar_node`
(`/livox/imu`) ergänzt — beides sind reale Topics, die die jeweiligen
echten Treiber (realsense2_camera, livox_ros_driver2) ohnehin publizieren.

**Wichtig für alle Downstream-Nodes:** `frame_transform_node` &
Co. zielen auf `mast_base_link`, **nicht** `mast_platform_link` — die
Plattform pant, würde man das Terrain-Grid relativ zu ihr aufbauen, würde
sich die Karte bei jeder Pan-Bewegung mitdrehen statt eine stabile Karte
über mehrere Blickrichtungen aufzubauen. `mast_base_link` bewegt sich nur
bei echter Mast-Neigung (quasi-statisch).

**Noch offen:** Position der Hardware-Box / des Mast-Fußpunkts (nur
Rotation wird aktuell korrigiert, Translation `world → mast_base_link`
bleibt Platzhalter `(0,0,0)`) — laut Absprache ein späteres Thema.

## Pipeline (Lidar + Stereo)

```
fake_lidar_node (rover_lidar)  ──────────────────────────────┐
                                                              v
                                              frame_transform_node ──> pointcloud_preprocessing_node ──┐
                                              (lidar, target=mast_base_link)  (crop/voxel/outlier)       │
                                                                                                         v
fake_stereo_camera_node ──> stereo_pointcloud_node ──> frame_transform_node ──> pointcloud_preprocessing_node ──> global_pointcloud_fusion_node ──> obstacle_grid_node
  (Depth+CameraInfo,          (Pinhole-Backprojektion)   (stereo, target=mast_base_link) (crop/voxel/outlier)     (sync + concat)                    (Elevation-Grid,
   realsense2_camera-kompatibel)                                                                                                                     Traversability -> OccupancyGrid)
```

Statische TF (`static_transform_publisher`) liefert `mast_platform_link ->
lidar_frame` und `mast_platform_link -> camera_depth_optical_frame` mit
Platzhalter-Extrinsics (siehe `launch/stereo_lidar_fusion.launch.py`) —
**müssen noch vermessen/kalibriert werden.** `mast_pose_node` liefert den
dynamischen Teil davor (`world -> mast_base_link -> mast_platform_link`,
siehe oben).

**Persistenter Punkte-Puffer in `obstacle_grid_node`:** `global_pointcloud_
fusion_node` liefert nur eine Momentaufnahme (Lidar+Stereo synchronisiert auf
einen Zeitpunkt). Damit das Grid über mehrere Callbacks/Pan-Positionen hinweg
ein vollständiges Bild aufbaut statt bei jedem neuen Frame wieder bei null
anzufangen, hält `obstacle_grid_node` jetzt einen eigenen State: pro Zelle
einen `deque(maxlen=max_points_per_cell)`-Puffer (Default 50 Punkte/Zelle,
kontinuierlich gleitendes Fenster, ältester Punkt fällt zuerst raus).
`terrain_analysis.py` selbst bleibt unverändert/zustandslos — es bekommt bei
jedem Callback einfach mehr Punkte (den ganzen Puffer statt nur die neueste
Message).

## Mono-Cam/LED-Zweig (im Aufbau)

```
fake_mono_camera_node ──> led_detector_node ──> (position_rover_node, noch nicht gebaut)
  (rgb8, mast-montiert)     (Blob-Erkennung:
                              Helligkeit + Größe
                              -> Zentroid, Farbe,
                              Sichtstrahl)
```

Der Rover trägt ein bekanntes LED-Muster (3-5 LEDs, feste geometrische
Anordnung). `led_detector_node` findet einzelne Blobs im Bild und gibt pro
Blob Pixel-Position, Farbe und einen normierten Sichtstrahl aus — **keine**
Position, da eine Mono-Cam nur eine Richtung liefert. Aus dem erkannten
*Muster* (mehrere Blobs, deren relative Anordnung mit dem bekannten
Muster verglichen wird) Abstand und Position des Rovers relativ zum Mast
zu berechnen (klassisches PnP-Problem, wie bei Motion-Capture-Markern) ist
Aufgabe von `position_rover_node`, die noch nicht existiert.

`fake_mono_camera_node`s aktuelle Fake-Szene (unabhängig driftende Blobs)
bildet das noch nicht korrekt ab — wird als Nächstes auf ein starres,
sich gemeinsam bewegendes LED-Muster umgebaut, plus Einbindung der
Mono-Cam-TF (`mast_link -> mono_cam_optical_frame`) ins Launch-File.

## Wichtigste Architektur-Änderung ggü. deinem Diagramm

Dein Entwurf hatte pro Sensor-Zweig eigene "pose"-Pfeile
(Int_pose_node → turn_pointcloud_node / stereo-Zweig / position_rover_node).
Das ist durch den ROS2-TF2-Baum ersetzt:

- Ein einziger, generischer `frame_transform_node` (statt mehrerer
  Spezial-Knoten), zweimal instanziiert (Lidar, Stereo) mit unterschiedlichen
  Launch-Parametern.
- Aktuell nur statische Transforms. Sobald IMU-Fusion/Lokalisierung existiert,
  publisht sie einfach dynamische Transforms in denselben TF-Baum —
  `frame_transform_node` selbst muss dafür nicht geändert werden.
- Broadcast von Punktwolken zwischen Knoten läuft direkt über Topics, nicht
  über einen manuell mitgeführten Pose-Topic.

## Hardware-Swap (Fake -> Real)

- **Lidar (Livox Mid-360S):** `fake_lidar_node` publisht bereits exakt wie
  `livox_ros_driver2` (Topic `/livox/points`). Swap = fake-Node aus Launch
  entfernen, `livox_ros_driver2` starten. Mid-360S hängt am Ethernet/UDP,
  nicht USB — braucht eigene Netzwerkkonfiguration (statische IP
  `192.168.1.1XX`), nicht Teil dieser Pipeline.
- **Stereo (RealSense D400, vermutlich D435i):** `fake_stereo_camera_node`
  publisht Topics/Encoding/Frame-Konvention (REP-103, Z vorwärts) identisch zu
  `realsense2_camera`. Swap = fake-Node entfernen, `realsense2_camera` starten.
  Die eingebaute IMU (BMI055) ist noch nicht eingebunden (siehe unten).

## Offene Punkte (bewusst nicht in Phase 1)

1. **Stereo "tbd/optional"-Stufe** aus dem Diagramm (zwischen stereo_camera_node
   und make_point_cloud_node, z.B. Temporal-Filter/Hole-Filling) — nichts
   Konkretes zum Implementieren vorhanden, aktuell übersprungen.
2. ~~**IMU-Fusion / Int_pose_node**~~ **Erledigt** — `mast_pose_node`
   (siehe "Pan/Tilt-Kinematik" oben). Offen bleibt nur die *Position*
   der Hardware-Box/des Mastfußes (Translation `world -> mast_base_link`),
   bewusst als späteres Thema zurückgestellt.
3. **position_rover_node** (Muster-Matching + PnP-Posenschätzung aus den
   `led_detector_node`-Blobs): noch nicht gebaut, siehe "Mono-Cam/LED-Zweig"
   oben.
4. **Comms-Kette** (WIFI_jetson_node <-> com_encoder_node <-> Commander_node
   <-> Data_storage_node/bridge_STM_node): out of scope für Phase 1, existiert
   teilweise schon in `rover_control` — perspektivisch der Weg, über den
   `position_rover_node`s Ergebnis an den echten Rover zurückgemeldet wird.
5. **Kalibrierung:** Static-TF-Extrinsics in `stereo_lidar_fusion.launch.py`
   sind Platzhalter — müssen durch echte Vermessung/Kalibrierung ersetzt
   werden, bevor die Fusion vertrauenswürdig ist.

## Nebenbei gefixt

`rover_lidar/package.xml` fehlten Dependencies (`sensor_msgs_py`, `nav_msgs`,
`python3-numpy`, `python3-scipy`), obwohl `lidar_processing_node.py` sie
importiert/nutzt — ergänzt.
