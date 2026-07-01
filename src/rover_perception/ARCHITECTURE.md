# rover_perception – Architektur

Für eine vollständige Liste aller Topics/Messages (inkl. Feldbeschreibung
der custom `TerrainGrid`-Message) siehe `README.md`.

Phase 1 ("Stereo+Lidar Fusion zuerst"). Mono-Cam/LED, IMU-Fusion und die
Comms-Kette aus dem ursprünglichen Diagramm sind bewusst noch nicht
implementiert (siehe "Offene Punkte" unten).

## Pipeline

```
fake_lidar_node (rover_lidar)  ──────────────────────────────┐
                                                              v
                                              frame_transform_node ──> pointcloud_preprocessing_node ──┐
                                              (lidar, target=base_link)   (crop/voxel/outlier)          │
                                                                                                         v
fake_stereo_camera_node ──> stereo_pointcloud_node ──> frame_transform_node ──> pointcloud_preprocessing_node ──> global_pointcloud_fusion_node ──> obstacle_grid_node
  (Depth+CameraInfo,          (Pinhole-Backprojektion)   (stereo, target=base_link) (crop/voxel/outlier)         (sync + concat)                    (Elevation-Grid,
   realsense2_camera-kompatibel)                                                                                                                     Traversability -> OccupancyGrid)
```

Statische TF (`static_transform_publisher`) liefert `base_link -> lidar_frame`
und `base_link -> camera_depth_optical_frame` mit Platzhalter-Extrinsics
(siehe `launch/stereo_lidar_fusion.launch.py`) — **müssen noch vermessen/kalibriert werden.**

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
2. **IMU-Fusion / Int_pose_node** (Mast-IMU + Stereo-IMU -> dynamische Pose):
   noch nicht gebaut. Sobald vorhanden: dynamische TF-Transforms publishen,
   `frame_transform_node` braucht keine Änderung.
3. **Mono-Cam/LED-Erkennung** (mono_cam_node -> led_detector_node ->
   position_rover_node): out of scope für Phase 1.
4. **Comms-Kette** (WIFI_jetson_node <-> com_encoder_node <-> Commander_node
   <-> Data_storage_node/bridge_STM_node): out of scope für Phase 1, existiert
   teilweise schon in `rover_control`.
5. **Kalibrierung:** Static-TF-Extrinsics in `stereo_lidar_fusion.launch.py`
   sind Platzhalter — müssen durch echte Vermessung/Kalibrierung ersetzt
   werden, bevor die Fusion vertrauenswürdig ist.

## Nebenbei gefixt

`rover_lidar/package.xml` fehlten Dependencies (`sensor_msgs_py`, `nav_msgs`,
`python3-numpy`, `python3-scipy`), obwohl `lidar_processing_node.py` sie
importiert/nutzt — ergänzt.
