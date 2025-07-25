import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
import pretty_midi
import subprocess
import time

def open_file(filepath):
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":  # macOS
        subprocess.call(["open", filepath])
    else:  # Linux & andere
        subprocess.call(["xdg-open", filepath])

def mxl_to_midi(filename, log_callback=print):
    def log(*args):
        log_callback(" ".join(str(a) for a in args) + "\n")
    
    MXL_PATH  = f"./MXL/{filename}/{filename}.mxl"
    XML_FILE  = f"./XML/{filename}.xml"

    # 1. MXL entpacken
    with zipfile.ZipFile(MXL_PATH) as archive:
        for name in archive.namelist():
            if name.endswith(".xml"):
                with archive.open(name) as xml_in:
                    xml_bytes = xml_in.read()
                    root      = ET.fromstring(xml_bytes)
                    xml_str   = ET.tostring(root, encoding="utf-8").decode("utf-8")
                    with open(XML_FILE, "w", encoding="utf-8") as f:
                        f.write(xml_str)
                log(f"✅ MusicXML gespeichert: {XML_FILE}")
                break

    # 2. MusicXML laden & BPM ermitteln
    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    def tag(e):  # Namespace abstreifen
        return e.tag.split("}")[-1] if "}" in e.tag else e.tag

    def find_bpm(r):
        for sound in r.findall(".//sound"):
            tempo = sound.get("tempo")
            if tempo:
                try:
                    return float(tempo)
                except ValueError:
                    pass
        for pm in r.findall(".//metronome/per-minute"):
            try:
                return float(pm.text)
            except (ValueError, TypeError):
                pass
        return None

    BPM = find_bpm(root) or 120.0
    BEAT_SEC = 60.0 / BPM
    log(f"Erkannte BPM: {BPM}")

    # 3. Instrumente pro Part
    part_instruments = {}
    for sp in root.findall("part-list/score-part"):
        pid = sp.get("id")
        prog = sp.find("midi-instrument/midi-program")
        part_instruments[pid] = int(prog.text) if prog is not None else 0

    # 4. Datencontainer
    midi_data = defaultdict(list)

    # 5. Hauptdurchlauf
    for part in root.findall("part"):
        part_id = part.get("id")

        divisions, beats_per_measure = 4, 4
        current_clef = "G"

        cursor = 0.0
        current_times = defaultdict(float)
        last_start_per_voice = defaultdict(float)
        ties = defaultdict(dict)

        for measure in part.findall("measure"):

            attr = measure.find("attributes")
            if attr is not None:
                d = attr.find("divisions")
                if d is not None:
                    divisions = int(d.text)
                t = attr.find("time")
                if t is not None and t.find("beats") is not None:
                    beats_per_measure = int(t.find("beats").text)
                clef = attr.find("clef/sign")
                if clef is not None and clef.text:
                    current_clef = clef.text

            for elem in measure:
                el = tag(elem)

                if el in ("backup", "forward"):
                    dur = int(elem.find("duration").text)
                    delta = (dur / divisions) * BEAT_SEC
                    cursor += -delta if el == "backup" else delta
                    continue

                if el != "note":
                    continue

                voice = elem.findtext("voice", default="1")

                if current_times[voice] < cursor:
                    current_times[voice] = cursor

                if elem.find("rest") is not None:
                    dur = int(elem.find("duration").text)
                    if elem.find("rest").get("measure") == "yes":
                        dur = divisions * beats_per_measure
                    current_times[voice] += (dur / divisions) * BEAT_SEC
                    cursor = max(cursor, current_times[voice])
                    continue

                dur = int(elem.find("duration").text)
                sec = (dur / divisions) * BEAT_SEC
                is_chord = elem.find("chord") is not None

                start_t = last_start_per_voice[voice] if is_chord else current_times[voice]
                end_t = start_t + sec
                if not is_chord:
                    last_start_per_voice[voice] = start_t
                    current_times[voice] = end_t
                    cursor = max(cursor, end_t)

                pitch = elem.find("pitch")
                step = pitch.find("step").text
                octave = int(pitch.find("octave").text)
                alter = int(pitch.find("alter").text) if pitch.find("alter") is not None else 0
                base = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[step]
                midi_note = base + alter + (octave + 1) * 12
                if current_clef == "F":
                    midi_note -= 12

                tie_types = {t.get("type") for t in elem.findall("tie")}
                if "stop" in tie_types and "start" not in tie_types:
                    for i in range(len(midi_data[(part_id, voice)])-1, -1, -1):
                        if midi_data[(part_id, voice)][i]["note"] == midi_note:
                            midi_data[(part_id, voice)][i]["end"] = end_t
                            break
                    continue

                velocity = 50 if elem.find("notations/slur") is not None else 64
                channel = (int(part_id[1:]) + int(voice)) % 16 if part_id.startswith("P") else 0

                midi_data[(part_id, voice)].append({
                    "note": midi_note,
                    "start": start_t,
                    "end": end_t,
                    "velocity": velocity,
                    "channel": channel,
                    "program": part_instruments.get(part_id, 0),
                })

    # 6. MIDI schreiben
    pm = pretty_midi.PrettyMIDI(resolution=480, initial_tempo=BPM)

    for (pid, voice), notes in midi_data.items():
        name = f"{pid}_V{voice}"
        instr = pretty_midi.Instrument(program=part_instruments.get(pid,0), name=name)
        for n in notes:
            instr.notes.append(pretty_midi.Note(
                velocity=n["velocity"],
                pitch=n["note"],
                start=n["start"],
                end=n["end"],
            ))
        pm.instruments.append(instr)

    out = f"./MIDI/{filename}.mid"
    pm.write(out)
    log(f"✅ MIDI-Datei gespeichert: {out}")
    time.sleep(0.3)  # kleine Wartezeit zur Sicherheit
    try:
        open_file(os.path.abspath(out))  # Direkt abspielen
    except Exception as e:
        log(f"❌ Fehler beim Öffnen der Datei: {e}")
    
