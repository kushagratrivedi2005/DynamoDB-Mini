# Hash Ring Visualization Scripts

Beautiful visualization system for the distributed hash ring with animations.

## Quick Start

```bash
# 1. Start system
./start_machine1.sh

# 2. Allocate nodes (in test terminal: option 2, enter 3)

# 3. Run operations
python3 run_100_operations.py

# 4. Generate visualization
python3 hash_ring_viz.py --frames

# 5. Create animation
python3 generate_animation.py

# 6. View
open hash_ring_animation.mp4
```

## Features

- 🎨 Beautiful circular hash ring with vibrant colors
- 🌈 3 distinct colors for physical machines (Purple, Cyan, Coral)
- ⚡ 60 virtual nodes (20 per machine)
- 🎬 Animated PUT/GET operations
- 📊 Quorum visualization (N=60, R=40, W=30)

## Files

- `hash_ring_viz.py` - Main visualization engine
- `generate_animation.py` - Animation creator
- `run_100_operations.py` - Automated test runner (in test/)

## Documentation

See [VISUALIZATION_GUIDE.md](../VISUALIZATION_GUIDE.md) for complete instructions.

## Requirements

```bash
pip install matplotlib numpy imageio imageio-ffmpeg pillow
```
