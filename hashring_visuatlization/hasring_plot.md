# Hash Ring Node Join/Leave Simulation Guide

Complete guide for generating simulated animations of nodes joining and leaving the hash ring at different scales.

## 🎯 Overview

This system creates **simulated** animations showing:
- Machines joining the hash ring
- Machines leaving the hash ring
- Node redistribution during changes
- Works at multiple scales: 10, 100, 1000, and 10000 nodes per machine

**No actual distributed system needed!** Pure simulation.

## 📋 Prerequisites

```bash
# Ensure you have the required packages
pip install matplotlib numpy imageio imageio-ffmpeg pillow
```

## 🚀 Quick Start - All 4 Scales

Run this to generate all 4 simulations:

```bash
cd /Users/hellgamerhell/Downloads/ds-majorproject/hashring_visuatlization

# 1. 10 nodes per machine
python3 simulate_ring_dynamics.py --nodes 10 --duration 10 --fps 10
python3 generate_animation.py --frames-dir simulation_frames_10nodes --output simulation_10nodes --fps 10

# 2. 100 nodes per machine
python3 simulate_ring_dynamics.py --nodes 100 --duration 10 --fps 10
python3 generate_animation.py --frames-dir simulation_frames_100nodes --output simulation_100nodes --fps 10

# 3. 1000 nodes per machine
python3 simulate_ring_dynamics.py --nodes 1000 --duration 10 --fps 10
python3 generate_animation.py --frames-dir simulation_frames_1000nodes --output simulation_1000nodes --fps 10

# 4. 10000 nodes per machine
python3 simulate_ring_dynamics.py --nodes 10000 --duration 10 --fps 10
python3 generate_animation.py --frames-dir simulation_frames_10000nodes --output simulation_10000nodes --fps 10
```

## 📖 Detailed Instructions

### Step 1: Generate Simulation Frames

The simulation script creates a random walk of machines joining and leaving:

```bash
python3 simulate_ring_dynamics.py --nodes <NUM_NODES> [OPTIONS]
```

**Arguments:**
- `--nodes`: Number of virtual nodes per machine (10, 100, 1000, 10000)
- `--machines`: Maximum number of machines (default: 3)
- `--events`: Number of join/leave events (default: 20)
- `--duration`: Animation duration in seconds (default: 10)
- `--fps`: Frames per second (default: 10)
- `--output`: Output directory prefix (default: simulation_frames)

**Example - 10 nodes per machine:**
```bash
python3 simulate_ring_dynamics.py --nodes 10 --duration 10 --fps 10
```

**Output:**
```
============================================================
  HASH RING SIMULATION
  10 nodes/machine | 3 max machines
============================================================

🎲 Generating random walk with 20 events...
✓ Created 20 events

Events:
  1. Machine 0 joins
  2. Machine 1 joins
  3. Machine 2 leaves
  ...

🎬 Generating 100 frames for 20 events...
   Duration: 10s @ 10 FPS
   Generated 20/100 frames...
   Generated 40/100 frames...
   ...
✅ Generated 100 frames in simulation_frames_10nodes/
```

### Step 2: Create Animation

Convert the frames into an MP4 animation:

```bash
python3 generate_animation.py --frames-dir simulation_frames_<NODES>nodes --output simulation_<NODES>nodes --fps 10
```

**Example - 10 nodes:**
```bash
python3 generate_animation.py --frames-dir simulation_frames_10nodes --output simulation_10nodes --fps 10
```

**Output:**
```
============================================================
  HASH RING ANIMATION GENERATOR
============================================================

📁 Found 100 frames in simulation_frames_10nodes/
🎬 Creating MP4 animation at 10.0 FPS...

✅ ANIMATION CREATED SUCCESSFULLY!
============================================================
  Output: simulation_10nodes.mp4
  Duration: ~10.0 seconds
  FPS: 10.0
============================================================
```

### Step 3: View Animations

```bash
# 10 nodes
open simulation_10nodes.mp4

# 100 nodes
open simulation_100nodes.mp4

# 1000 nodes
open simulation_1000nodes.mp4

# 10000 nodes
open simulation_10000nodes.mp4
```

## 🎨 What You'll See

### 10 Nodes Per Machine
- **Clearly visible** individual virtual nodes
- **Labels shown** for each vnode (v0, v1, v2, ...)
- **Easy to track** node redistribution
- Perfect for understanding the algorithm

### 100 Nodes Per Machine
- **Smaller nodes** without labels
- **Still distinguishable** individual points
- **Shows density** differences clearly
- Good balance of detail and scale

### 1000 Nodes Per Machine
- **Dense ring** of small points
- **Color bands** become visible
- **Demonstrates** load balancing at scale
- Realistic production-like visualization

### 10000 Nodes Per Machine
- **Very dense** continuous-looking ring
- **Smooth color distribution**
- **Shows** extreme scale behavior
- Visualizes massive distributed systems

## 🎬 Animation Features

Each animation shows:
1. **Initial state**: First machine joins
2. **Random walk**: Machines join and leave randomly
3. **Node redistribution**: Watch vnodes redistribute as machines change
4. **Color coding**: Each machine has a distinct vibrant color
5. **Event descriptions**: See what's happening at each step
6. **Node counts**: Total virtual nodes displayed

## ⚙️ Customization Options

### Longer Animations
```bash
python3 simulate_ring_dynamics.py --nodes 10 --duration 20 --fps 10
```

### More Events
```bash
python3 simulate_ring_dynamics.py --nodes 10 --events 40
```

### Different Machine Count
```bash
python3 simulate_ring_dynamics.py --nodes 100 --machines 5
```

### Create GIF Instead
```bash
python3 generate_animation.py --frames-dir simulation_frames_10nodes --output simulation_10nodes --format gif
```

## 📁 Output Files

After running all simulations, you'll have:

```
code/
├── simulation_frames_10nodes/      # 100 PNG frames
│   ├── frame_0000.png
│   ├── frame_0001.png
│   └── ...
├── simulation_frames_100nodes/     # 100 PNG frames
├── simulation_frames_1000nodes/    # 100 PNG frames
├── simulation_frames_10000nodes/   # 100 PNG frames
├── simulation_10nodes.mp4          # 10-second animation
├── simulation_100nodes.mp4         # 10-second animation
├── simulation_1000nodes.mp4        # 10-second animation
└── simulation_10000nodes.mp4       # 10-second animation
```

## 🎯 Batch Generation Script

Create all 4 animations at once:

```bash
#!/bin/bash
cd /Users/hellgamerhell/Downloads/ds-majorproject/code

echo "Generating simulations for all scales..."

for nodes in 10 100 1000 10000; do
    echo ""
    echo "========== $nodes nodes per machine =========="
    
    echo "1. Generating frames..."
    python3 simulate_ring_dynamics.py --nodes $nodes --duration 10 --fps 10
    
    echo "2. Creating animation..."
    python3 generate_animation.py --frames-dir simulation_frames_${nodes}nodes \
                                  --output simulation_${nodes}nodes --fps 10
    
    echo "✅ Completed $nodes nodes simulation"
done

echo ""
echo "🎉 All simulations complete!"
echo ""
echo "View animations:"
echo "  open simulation_10nodes.mp4"
echo "  open simulation_100nodes.mp4"
echo "  open simulation_1000nodes.mp4"
echo "  open simulation_10000nodes.mp4"
```

Save as `generate_all_simulations.sh` and run:
```bash
chmod +x generate_all_simulations.sh
./generate_all_simulations.sh
```

## 💡 Tips

1. **Frame Quality**: Frames are saved at 100 DPI for fast generation. Increase for higher quality
2. **Animation Speed**: Use `--fps 5` for slower, more detailed viewing
3. **File Size**: MP4 files are smaller than GIFs (~0.5 MB vs ~5 MB)
4. **Custom Seeds**: Modify the random seed in the code for different join/leave patterns

## 🔍 Understanding the Simulations

### Random Walk Algorithm
1. Start with 1 machine
2. At each step, randomly choose to:
   - **Join**: Add a new machine (if < max_machines)
   - **Leave**: Remove a random machine (if > 1 machine)
3. Continue for N events

###Hash Ring Dynamics
- **Join**: New virtual nodes are added to the ring
- **Leave**: Virtual nodes are removed, keys redistribute to next node clockwise
- **Load balancing**: More nodes = better key distribution

## 🎓 Educational Use

Perfect for demonstrating:
- Consistent hashing concepts
- Distributed system scalability
- Node failure and recovery
- Load balancing across machines
- Virtual nodes technique

---

**Quick Reference:**
```bash
# Generate frames
python3 simulate_ring_dynamics.py --nodes <10|100|1000|10000> --duration 10 --fps 10

# Create animation
python3 generate_animation.py --frames-dir simulation_frames_<N>nodes --output simulation_<N>nodes --fps 10

# View
open simulation_<N>nodes.mp4
```
