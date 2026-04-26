# PHYC2050 Traffic Flow Final Project

This project simulates traffic through two intersection controls:

- a four-arm roundabout
- a two-road traffic light with opposite horizontal/vertical phases

The report source is `report.tex`. Figures are stored in `figures/`, movies are
stored in `animations/`, and all simulation/analysis code is in `code/`.

## Requirements

The Python scripts require:

- Python 3
- NumPy
- Matplotlib
- FFmpeg, only for regenerating `.mp4` animations

Install the Python packages with:

```bash
pip install -r requirements.txt
```

## Regenerating Outputs

Run scripts from the `code/` directory so the relative output paths resolve:

```bash
cd code
python analysis1_roundabout_baseline.py
python analysis2_roundabout_density.py
python analysis3_roundabout_asymmetric.py
python analysis4_roundabout_hv_difference.py
python analysis5_lights_density_and_cycle.py
python analysis6_roundabout_vs_lights.py
python analysis7_lights_asymmetric.py
python analysis8_lights_hv_difference.py
python analysis9_flow_rate_comparison.py
python anim_lights.py
python anim_roundabout.py
```

The main outputs used by the report are already included in `figures/` and
`animations/`.
