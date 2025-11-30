#!/bin/bash
# Batch generate all 4 scale simulations
# 10, 100, 1000, and 10000 nodes per machine

cd "$(dirname "$0")"

echo "============================================================"
echo "  HASH RING SIMULATION - ALL SCALES"
echo "  Generating 10, 100, 1000, and 10000 node simulations"
echo "============================================================"
echo ""

for nodes in 10 100 1000 10000; do
    echo ""
    echo "=========================================="
    echo "  $nodes nodes per machine"
    echo "=========================================="
    
    echo "📊 Step 1/2: Generating frames..."
    python3 script.py --nodes $nodes --duration 10 --fps 10
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate frames for $nodes nodes"
        continue
    fi
    
    echo ""
    echo "🎬 Step 2/2: Creating animation..."
    python3 generate_animation.py --frames-dir simulation_frames_${nodes}nodes \
                                  --output simulation_${nodes}nodes --fps 10
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create animation for $nodes nodes"
        continue
    fi
    
    echo "✅ Completed $nodes nodes simulation"
done

echo ""
echo "============================================================"
echo "  🎉 ALL SIMULATIONS COMPLETE!"
echo "============================================================"
echo ""
echo "Generated animations:"
echo "  • simulation_10nodes.mp4     (10 vnodes/machine)"
echo "  • simulation_100nodes.mp4    (100 vnodes/machine)"
echo "  • simulation_1000nodes.mp4   (1000 vnodes/machine)"
echo "  • simulation_10000nodes.mp4  (10000 vnodes/machine)"
echo ""
echo "To view:"
echo "  open simulation_10nodes.mp4"
echo "  open simulation_100nodes.mp4"
echo "  open simulation_1000nodes.mp4"
echo "  open simulation_10000nodes.mp4"
echo ""
