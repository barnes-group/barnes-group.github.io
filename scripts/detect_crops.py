#!/usr/bin/env python3
"""Suggest a vertical crop for every exported screenshot so that content stays legible when
the framed screen is shown small. Writes scripts/crops.json (name -> [top, bottom] as fractions of the height).
Manual overrides at the bottom win over the automatic result."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCREENS = ROOT / "g25/assets/img/screens"
H = 960
HEADER = 66      # status header + page title
FOOTER = 842     # tab bar and footer start

# name -> (top, bottom) as fractions of the screenshot height; for dialogs, keypads and short screens
OVERRIDES = {
    "dashboard_all_zones_on": (0, 0.42),
    "dashboard_zones_reaching_target": (0, 0.42),
    "dashboard_table": (0, 0.62),
    "material_apply": (0.34, 0.66),
    "add_material_modal_filled": (0.32, 0.74),
    "boost_dialog": (0.38, 0.66),
    "standby_dialog": (0.36, 0.68),
    "analog_inputs_channel_alarm_modal": (0.30, 0.76),
    "setpoint_change_some_zones_keypad": (0.40, 0.92),
    "quick_mold": (0.20, 0.64),
    "leak_detection_alarm": (0, 0.50),
    "mold_doctor": (0, 0.40),
    "mold_doctor_wiring_analysis_completed": (0, 0.40),
    "mold_doctor_fault_analysis_completed": (0, 0.40),
    "mold_doctor_tda_completed": (0, 0.50),
    "mold_doctor_historic_analysis_both_chosen": (0, 0.55),
    "mold_doctor_tuning_analysis": (0, 0.90),
    "mold_wizard": (0, 0.55),
    "mold_wizard_discovery_completed": (0, 0.80),
    "tools_and_diagnostics_econtrol": (0, 0.72),
    "tools_and_diagnostics_historical_data": (0, 0.62),
    "process_and_hardware_opcua_options": (0, 0.65),
    "process_and_hardware_remote_io_remote_io_expanded": (0, 0.45),
}


def content_end(img):
    a = np.asarray(img.convert("RGB").resize((540, H)), dtype=np.int16)
    med = np.median(a, axis=1, keepdims=True)
    diff = np.sqrt(((a - med) ** 2).sum(axis=2))
    rows = (diff > 38).sum(axis=1)
    active = np.where(rows[HEADER:FOOTER] > 6)[0]
    return HEADER + int(active.max()) if len(active) else H


def main():
    crops = {}
    for f in sorted(SCREENS.glob("*-sm.webp")):
        name = f.name[:-8]
        end = content_end(Image.open(f))
        top, bottom = 0, min(H, end + 40)
        if bottom > 700:
            top, bottom = 0, H
        bottom = max(bottom, 360)
        crops[name] = [round(top / H, 4), round(bottom / H, 4)]
    for name, (t, b) in OVERRIDES.items():
        crops[name] = [t, b]
    (ROOT / "scripts/crops.json").write_text(json.dumps(crops, indent=1))
    for k, v in crops.items():
        print(f"{k:60s} {v}")


if __name__ == "__main__":
    main()
