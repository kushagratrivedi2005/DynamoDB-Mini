#!/usr/bin/env python3
"""
Hash Ring Animation Generator

Creates smooth MP4 and GIF animations from generated frames showing
PUT/GET operations on the distributed hash ring.

Requirements:
    pip install imageio imageio-ffmpeg pillow

Usage:
    python3 generate_animation.py [--fps 2] [--format mp4]
"""

import os
import argparse
import imageio
from pathlib import Path
import glob

def create_animation(frames_dir='frames', output_name='hash_ring_animation', 
                    fps=2, format='mp4', repeat_last=3):
    """
    Create animation from frames
    
    Args:
        frames_dir: Directory containing frame images
        output_name: Base name for output file
        fps: Frames per second
        format: Output format ('mp4' or 'gif')
        repeat_last: Number of times to repeat the last frame
    """
    
    print("=" * 60)
    print("  HASH RING ANIMATION GENERATOR")
    print("=" * 60)
    print()
    
    # Get all frame files
    frame_pattern = os.path.join(frames_dir, 'frame_*.png')
    frame_files = sorted(glob.glob(frame_pattern))
    
    if not frame_files:
        print(f"❌ No frames found in {frames_dir}/")
        print(f"   Run visualization first: python3 hash_ring_viz.py --frames")
        return
    
    print(f"📁 Found {len(frame_files)} frames in {frames_dir}/")
    print(f"🎬 Creating {format.upper()} animation at {fps} FPS...")
    print()
    
    # Read frames
    print("📖 Reading frames...")
    frames = []
    for i, frame_file in enumerate(frame_files):
        img = imageio.imread(frame_file)
        frames.append(img)
        
        if (i + 1) % 20 == 0:
            print(f"   Read {i + 1}/{len(frame_files)} frames...")
    
    # Add repeated last frame for better viewing
    if frames and repeat_last > 0:
        print(f"🔄 Adding {repeat_last}s pause at end...")
        last_frame = frames[-1]
        for _ in range(int(repeat_last * fps)):
            frames.append(last_frame)
    
    print()
    
    # Create output
    if format.lower() == 'mp4':
        output_file = f'{output_name}.mp4'
        print(f"💾 Saving MP4 to {output_file}...")
        
        # Use imageio to create MP4
        imageio.mimsave(output_file, frames, fps=fps, quality=8, 
                       codec='libx264', pixelformat='yuv420p')
        
    elif format.lower() == 'gif':
        output_file = f'{output_name}.gif'
        print(f"💾 Saving GIF to {output_file}...")
        
        # Create GIF with imageio
        imageio.mimsave(output_file, frames, fps=fps, loop=0)
    
    else:
        print(f"❌ Unsupported format: {format}")
        print("   Supported formats: mp4, gif")
        return
    
    # Get file size
    file_size = os.path.getsize(output_file)
    size_mb = file_size / (1024 * 1024)
    
    print()
    print("=" * 60)
    print("  ✅ ANIMATION CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"  Output: {output_file}")
    print(f"  Size: {size_mb:.2f} MB")
    print(f"  Frames: {len(frame_files)}")
    print(f"  Duration: ~{len(frames) / fps:.1f} seconds")
    print(f"  FPS: {fps}")
    print("=" * 60)
    print()
    
    # Platform-specific viewing instructions
    import platform
    system = platform.system()
    
    print("🎥 To view the animation:")
    if system == 'Darwin':  # macOS
        print(f"   open {output_file}")
    elif system == 'Linux':
        print(f"   xdg-open {output_file}")
    else:  # Windows
        print(f"   start {output_file}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Generate animation from hash ring visualization frames'
    )
    parser.add_argument('--frames-dir', default='frames',
                       help='Directory containing frame images (default: frames)')
    parser.add_argument('--output', default='hash_ring_animation',
                       help='Output file name without extension (default: hash_ring_animation)')
    parser.add_argument('--fps', type=float, default=2.0,
                       help='Frames per second (default: 2.0)')
    parser.add_argument('--format', choices=['mp4', 'gif'], default='mp4',
                       help='Output format (default: mp4)')
    parser.add_argument('--repeat-last', type=int, default=3,
                       help='Seconds to hold last frame (default: 3)')
    
    args = parser.parse_args()
    
    create_animation(
        frames_dir=args.frames_dir,
        output_name=args.output,
        fps=args.fps,
        format=args.format,
        repeat_last=args.repeat_last
    )


if __name__ == '__main__':
    main()
