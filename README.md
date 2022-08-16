# Project Stanley
---
Verwendete Libraries/Pakete:
numpy: https://numpy.org/
OpenCV: https://opencv.org/
mathplotlib: https://matplotlib.org/
PyToch: https://pytorch.org/ 
conda-forge: https://conda-forge.org/
anaconda: https://www.anaconda.com/ 
pip: https://pypi.org/project/pip/


Der Start des Servers zum Steuern des Autos erfolgt automatisch auf dem Rasperry Pi. Dies wurde mit einem cron Job auf dem Pi umgesetzt, welcher nach dem Start ausgeführt wird.
Über diesen Server werden die Befehle der nachfolgenden Dateien auf dem Pi und somit dem Fahrzeug ausgeführt.
Im folgenden werden alle Dateien und ihre Funktionsweise beschrieben.

Dateien: 
main.py:
-erstellt eine Instanz der "pi_car" Klasse aus der Datei "Pi_Car_Controls.py" --> Stuerung des Autos und der Kamera 
-erstellt Instanz der "video_streamer" Klasse aus der "Streaming_Controls.py" Datei --> Verfügbarmachung jeglichen Bildmaterial der Fahrzeugkamera
-Instanz der "stop_sign" Klasse aus der "Object_Detector.py" Datei für die Stopschilderkennung und der "person" Klasse für Personenerkennung
-für Verfolgung der Linien wird eine Instanz der "LineFollower" Klasse aus der "Line_Follower.py" Datei erstellt 

-keymapping, sprich eine Belegung der Tastatur Tasten, damit das Fahrzeug im manuellen Modus mit Tastaturbefehlen gesteuert werden kann
-callback_fnc Funktion wird aufgerufen, wenn eine Taste gedrückt wird. Es wird die Geschwindigkeit des Autos gesetzt und es kann zwischen manuellem und automatischem Modus umgeschaltet werden
-Hauptschleife ruftbenötigten Funktionen für die Linien/Stoppschild/Personen Erkennung auf, sowie die dadurch errechnete Steuerung wird ausgeführt

Line_Follower.py: 
-Beinhaltet alle Funktionen die zum Folgen der Linie notwendig sind
-Weitwinkelbilder der Kamera werden auf unteren Teil zurechtgeschnitten --> Vermeidung von Fehlerkennung
Kontrasterkennung einstellen:
-2 Kontrastfarbtöne sind einprogrammiert, um helle Linie oder dunkle Linie zu erkennen
-Linienmittelpunkt wird mit einem Kreis und damit X und Y Werten versehen
-Anhand dieser X und Y werte wird rechts und links gelenkt

Pi_Car_Controls.py:
-Beinhaltet alle Funktionen zur Steuerung des Fahrzeugs
-Des Weiteren können gradgenaue Lenkwinkel und Kamerawinkel eingestellt werden
-Außerdem kann die Geschwindigkeit des Autos eingestellt werden

Streaming_Controls.py:
-Beinhaltet alle Funktionen die dazu dienen das Kamerabild zu erhalten und verwertbar zu machen
