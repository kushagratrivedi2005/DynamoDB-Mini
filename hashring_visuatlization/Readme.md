# Hash Ring Simulation Animations - Quick Start

## What This Does

Creates beautiful animations showing how virtual nodes are distributed when machines join and leave a consistent hash ring at 4 different scales.

## Quick Generate All 4 Animations

```bash
cd /Users/hellgamerhell/Downloads/ds-majorproject/hashring_visuatlization
./generate_all_simulations.sh
```

This will create:
- `simulation_10nodes.mp4` - 10 virtual nodes per machine
- `simulation_100nodes.mp4` - 100 virtual nodes per machine  
- `simulation_1000nodes.mp4` - 1000 virtual nodes per machine
- `simulation_10000nodes.mp4` - 10000 virtual nodes per machine

Each animation is 10 seconds long showing machines randomly joining and leaving.

## View Animations

```bash
cd code
open simulation_10nodes.mp4
open simulation_100nodes.mp4
open simulation_1000nodes.mp4
open simulation_10000nodes.mp4
```

## Manual Generation (One Scale at a Time)

### Generate Frames
```bash
python3 simulate_ring_dynamics.py --nodes <10|100|1000|10000> --duration 10 --fps 10
```

### Create Animation
```bash
python3 generate_animation.py --frames-dir simulation_frames_<N>nodes --output simulation_<N>nodes --fps 10
```

## What You'll See

- **Circular hash ring** with color-coded machines
- **Machines joining** (vnodes appear)
- **Machines leaving** (vnodes disappear)  
- **Node redistribution** as ring changes
- **Beautiful dark theme** with vibrant colors

## Full Documentation

See [SIMULATION_GUIDE.md](../SIMULATION_GUIDE.md) for complete details.
