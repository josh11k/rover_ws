# rover_control – Message-/Topic-Referenz

Alle Nachrichten, die zur rover kontrolle laufen. Für die Gesamtarchitektur siehe
`ARCHITECTURE.md`.

---

### `/stm/set_mode_on_stm`
**Typ:** `rover_control_msgs/SetOperationalMode.srv`
**Client:** `command_node`
**Service:** `stm_bridge_node`
Nachricht enthält den vom Jetson geforderten Modus. Wird nur aufgerufen, wenn der Jetson den service anfragt. 
Enthält Feedback vom STM, ob der Node Wechsel erfolgreich war und in welchen Mode gewechselt wurde

### `/stm/feedback_of_stm`
**Typ:** `rover_contro_msgs/SetOperationalMode.msg`
**Publisher:** `stm_brige_node`
**Subscriber:** `command_node`
Enthält Feedback vom STM, welcher Modus gesetzt werden soll. Geht dann in funktion mode_feedback_callback, die den neuen opertional mode published.

### `/operational_mode/current`
**Typ:** `rover_control_msgs/CurrentOperationalMode`
**Publisher:**`command_node`
**Subscriber:** `set_mode_node`
Enthält den aktuellen Operational mode. Kann getriggert werden, falls der Jetson seinen Mode wechseln will oder falls der STM die Node wechseln will.

### `/operational_mode/settings`
**Typ:** `rover_control_msgs/OperationalModeSettings.msg`
**Publisher:**`set_mode_node`
**Subscriber:** `eigneltich alle`
Enthält für jeden Modus die On, Off, Standby informationen für alle Komponenten. 

