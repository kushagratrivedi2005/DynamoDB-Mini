#!/usr/bin/env python3
"""
Log-Based Performance Analyzer

Extracts latency and throughput metrics from existing log files.
Works with both client.log (if instrumented) and worker logs (fallback).

Usage:
    python3 analyze_logs_latency.py
    python3 analyze_logs_latency.py --log-dir logs
"""

import re
import os
import sys
import argparse
from datetime import datetime
from collections import defaultdict
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LatencyAnalyzer:
    def __init__(self, log_dir='../logs'):
        self.log_dir = Path(log_dir)
        self.client_log = self.log_dir / 'client.log'
        self.worker_logs = list(self.log_dir.glob('worker_*.log'))
        
        # Data storage
        self.latencies = defaultdict(list)  # {op_type: [latencies]}
        self.timestamps = []  # All operation timestamps
        self.operations = []  # List of (timestamp, op_type, status)
        
    def parse_client_logs(self):
        """Parse client.log for LATENCY_START/END markers"""
        if not self.client_log.exists():
            print(f"{Colors.WARNING}⚠ client.log not found{Colors.ENDC}")
            return False
            
        print(f"\n{Colors.OKBLUE}📖 Parsing client.log...{Colors.ENDC}")
        
        start_times = {}  # request_id -> (timestamp, op_type)
        pattern = re.compile(
            r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .*? - '
            r'\[LATENCY_(?P<type>START|END)\] '
            r'request_id=(?P<id>[a-f0-9\-]+) '
            r'op=(?P<op>GET|PUT)'
            r'(?: status=(?P<status>SUCCESS|FAILURE))?'
        )
        
        with open(self.client_log, 'r') as f:
            for line in f:
                match = pattern.match(line.strip())
                if not match:
                    continue
                    
                data = match.groupdict()
                req_id = data['id']
                timestamp = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                
                if data['type'] == 'START':
                    start_times[req_id] = (timestamp, data['op'])
                    
                elif data['type'] == 'END' and req_id in start_times:
                    start_time, op_type = start_times.pop(req_id)
                    latency_ms = (timestamp - start_time).total_seconds() * 1000
                    
                    self.latencies[op_type].append(latency_ms)
                    self.timestamps.append(timestamp)
                    self.operations.append((timestamp, op_type, data.get('status', 'UNKNOWN')))
        
        total_ops = sum(len(v) for v in self.latencies.values())
        if total_ops > 0:
            print(f"{Colors.OKGREEN}✓ Found {total_ops} operations with latency data{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.WARNING}⚠ No latency markers found in client.log{Colors.ENDC}")
            return False
    
    def parse_worker_logs(self):
        """Fallback: Parse worker logs for operation timing"""
        if not self.worker_logs:
            print(f"{Colors.FAIL}❌ No worker logs found{Colors.ENDC}")
            return False
            
        print(f"\n{Colors.OKBLUE}📖 Parsing worker logs (fallback method)...{Colors.ENDC}")
        print(f"   Found {len(self.worker_logs)} worker log files")
        
        # UPDATED patterns to match the new log format with emoji markers
        # Example: 2025-11-30 21:31:21 - INFO - ⏱️  PUT START: key=key_001_t0fb value=... | timestamp=2025-11-30 21:31:21
        put_start_pattern = re.compile(
            r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - INFO - ⏱️\s+PUT START: key=(?P<key>\S+)'
        )
        
        # Example: 2025-11-30 21:31:21 - INFO - ✅ PUT COMPLETE: key=key_001_t0fb value=... | timestamp=... | duration=0.225s | status=SUCCESS | replicas=4
        put_end_pattern = re.compile(
            r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - INFO - [✅❌]\s+PUT COMPLETE: key=(?P<key>\S+).*\| duration=(?P<duration>[\d.]+)s \| status=(?P<status>\w+)'
        )
        
        # Example: 2025-11-30 21:31:21 - INFO - ⏱️  GET START: key=key_001_t0fb | timestamp=2025-11-30 21:31:21
        get_start_pattern = re.compile(
            r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - INFO - ⏱️\s+GET START: key=(?P<key>\S+)'
        )
        
        # Example: 2025-11-30 21:31:21 - INFO - ✅ GET COMPLETE: key=key_001_t0fb | timestamp=... | duration=0.225s | status=SUCCESS
        get_end_pattern = re.compile(
            r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - INFO - [✅❌]\s+GET COMPLETE: key=(?P<key>\S+).*\| duration=(?P<duration>[\d.]+)s \| status=(?P<status>\w+)'
        )
        
        total_puts_found = 0
        total_gets_found = 0
        
        for worker_log in self.worker_logs:
            print(f"   Processing {worker_log.name}...")
            pending_puts = {}  # key -> start_timestamp
            pending_gets = {}  # key -> start_timestamp
            
            try:
                with open(worker_log, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        
                        # Check for PUT start
                        match = put_start_pattern.search(line)
                        if match:
                            timestamp_str = match.group('timestamp')
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            key = match.group('key')
                            pending_puts[key] = timestamp
                            continue
                        
                        # Check for PUT end (extract duration directly from log!)
                        match = put_end_pattern.search(line)
                        if match:
                            key = match.group('key')
                            duration_s = float(match.group('duration'))
                            latency_ms = duration_s * 1000  # Convert to milliseconds
                            status = match.group('status')
                            
                            timestamp_str = match.group('timestamp')
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            
                            self.latencies['PUT'].append(latency_ms)
                            self.timestamps.append(timestamp)
                            self.operations.append((timestamp, 'PUT', status))
                            total_puts_found += 1
                            
                            # Clean up pending
                            pending_puts.pop(key, None)
                            continue
                        
                        # Check for GET start
                        match = get_start_pattern.search(line)
                        if match:
                            timestamp_str = match.group('timestamp')
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            key = match.group('key')
                            pending_gets[key] = timestamp
                            continue
                        
                        # Check for GET end (extract duration directly from log!)
                        match = get_end_pattern.search(line)
                        if match:
                            key = match.group('key')
                            duration_s = float(match.group('duration'))
                            latency_ms = duration_s * 1000  # Convert to milliseconds
                            status = match.group('status')
                            
                            timestamp_str = match.group('timestamp')
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            
                            self.latencies['GET'].append(latency_ms)
                            self.timestamps.append(timestamp)
                            self.operations.append((timestamp, 'GET', status))
                            total_gets_found += 1
                            
                            # Clean up pending
                            pending_gets.pop(key, None)
                                
            except Exception as e:
                print(f"{Colors.WARNING}   ⚠ Error reading {worker_log.name}: {e}{Colors.ENDC}")
                continue
        
        print(f"   Found {total_puts_found} PUT operations, {total_gets_found} GET operations")
        
        total_ops = sum(len(v) for v in self.latencies.values())
        if total_ops > 0:
            print(f"{Colors.OKGREEN}✓ Found {total_ops} operations from worker logs{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}❌ No operations found in worker logs{Colors.ENDC}")
            print(f"\n{Colors.WARNING}Debug info:{Colors.ENDC}")
            print(f"   Searched for patterns like:")
            print(f"   - '⏱️  PUT START: key=<key>'")
            print(f"   - '✅ PUT COMPLETE: key=<key> | duration=<seconds>s | status=<STATUS>'")
            print(f"   - '⏱️  GET START: key=<key>'")
            print(f"   - '✅ GET COMPLETE: key=<key> | duration=<seconds>s | status=<STATUS>'")
            print(f"\n{Colors.WARNING}Tip: Make sure your logs have the timing markers added by the updated worker.py{Colors.ENDC}")
            return False
    
    def calculate_statistics(self, data, label):
        """Calculate and print statistics for a dataset"""
        if not data:
            print(f"\n{Colors.WARNING}No data for {label}{Colors.ENDC}")
            return
        
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}  {label} Latency Statistics{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        print(f"  {Colors.OKCYAN}Sample Size:{Colors.ENDC} {len(data)} operations")
        print(f"  {Colors.OKCYAN}Average:{Colors.ENDC} {np.mean(data):.2f} ms")
        print(f"  {Colors.OKCYAN}Median (p50):{Colors.ENDC} {np.median(data):.2f} ms")
        print(f"  {Colors.OKCYAN}p95:{Colors.ENDC} {np.percentile(data, 95):.2f} ms")
        print(f"  {Colors.OKCYAN}p99:{Colors.ENDC} {np.percentile(data, 99):.2f} ms")
        print(f"  {Colors.OKCYAN}Min:{Colors.ENDC} {np.min(data):.2f} ms")
        print(f"  {Colors.OKCYAN}Max:{Colors.ENDC} {np.max(data):.2f} ms")
        print(f"  {Colors.OKCYAN}Std Dev:{Colors.ENDC} {np.std(data):.2f} ms")
    
    def calculate_throughput(self):
        """Calculate system throughput"""
        if len(self.timestamps) < 2:
            print(f"\n{Colors.WARNING}Not enough data to calculate throughput{Colors.ENDC}")
            return
        
        self.timestamps.sort()
        time_span = (self.timestamps[-1] - self.timestamps[0]).total_seconds()
        
        if time_span <= 0:
            print(f"\n{Colors.WARNING}All operations occurred in same second{Colors.ENDC}")
            return
        
        # Count successes and failures
        success_count = sum(1 for _, _, status in self.operations if status == 'SUCCESS')
        failure_count = sum(1 for _, _, status in self.operations if status == 'FAILURE')
        total_ops = len(self.operations)
        
        throughput = total_ops / time_span
        
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}  Throughput Analysis{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        print(f"  {Colors.OKCYAN}Total Operations:{Colors.ENDC} {total_ops}")
        print(f"  {Colors.OKGREEN}Successful:{Colors.ENDC} {success_count} ({success_count/total_ops*100:.1f}%)")
        if failure_count > 0:
            print(f"  {Colors.FAIL}Failed:{Colors.ENDC} {failure_count} ({failure_count/total_ops*100:.1f}%)")
        print(f"  {Colors.OKCYAN}Time Span:{Colors.ENDC} {time_span:.2f} seconds")
        print(f"  {Colors.OKGREEN}Throughput:{Colors.ENDC} {Colors.BOLD}{throughput:.2f} ops/sec{Colors.ENDC}")
        
        # Calculate per-operation-type throughput
        put_count = sum(1 for _, op, _ in self.operations if op == 'PUT')
        get_count = sum(1 for _, op, _ in self.operations if op == 'GET')
        
        if put_count > 0:
            print(f"  {Colors.OKCYAN}PUT Throughput:{Colors.ENDC} {put_count/time_span:.2f} ops/sec")
        if get_count > 0:
            print(f"  {Colors.OKCYAN}GET Throughput:{Colors.ENDC} {get_count/time_span:.2f} ops/sec")
    
    def plot_latency_distribution(self, output_dir='visualizations'):
        """Generate histogram showing PUT and GET latency distributions"""
        if not any(self.latencies.values()):
            print(f"\n{Colors.WARNING}⚠ No latency data available for plotting{Colors.ENDC}")
            return
        
        Path(output_dir).mkdir(exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = {'PUT': '#FF6B6B', 'GET': '#4ECDC4'}
        for op_type in ['PUT', 'GET']:
            if op_type in self.latencies and self.latencies[op_type]:
                data = self.latencies[op_type]
                ax.hist(data, bins=50, alpha=0.6, label=f'{op_type} (n={len(data)})', 
                       color=colors[op_type], edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Latency (ms)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Latency Distribution: GET vs PUT Operations', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        output_path = Path(output_dir) / 'latency_distribution.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✓ Saved latency distribution histogram: {output_path}{Colors.ENDC}")
    
    def plot_cdf(self, output_dir='visualizations'):
        """Generate cumulative distribution function plot with p95/p99 markers"""
        if not any(self.latencies.values()):
            print(f"\n{Colors.WARNING}⚠ No latency data available for plotting{Colors.ENDC}")
            return
        
        Path(output_dir).mkdir(exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = {'PUT': '#FF6B6B', 'GET': '#4ECDC4'}
        for op_type in ['PUT', 'GET']:
            if op_type in self.latencies and self.latencies[op_type]:
                data = np.array(sorted(self.latencies[op_type]))
                cdf = np.arange(1, len(data) + 1) / len(data)
                
                ax.plot(data, cdf, label=f'{op_type}', color=colors[op_type], linewidth=2)
                
                # Mark p95 and p99
                p95 = np.percentile(data, 95)
                p99 = np.percentile(data, 99)
                
                ax.axvline(p95, color=colors[op_type], linestyle='--', alpha=0.5, linewidth=1)
                ax.axhline(0.95, color='gray', linestyle=':', alpha=0.3, linewidth=1)
                ax.text(p95, 0.95, f'  p95={p95:.1f}ms', fontsize=9, 
                       verticalalignment='bottom', color=colors[op_type])
                
                ax.axvline(p99, color=colors[op_type], linestyle='--', alpha=0.5, linewidth=1)
                ax.axhline(0.99, color='gray', linestyle=':', alpha=0.3, linewidth=1)
                ax.text(p99, 0.99, f'  p99={p99:.1f}ms', fontsize=9, 
                       verticalalignment='bottom', color=colors[op_type])
        
        ax.set_xlabel('Latency (ms)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cumulative Probability', fontsize=12, fontweight='bold')
        ax.set_title('Cumulative Distribution Function (CDF) of Latency', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.02])
        
        output_path = Path(output_dir) / 'latency_cdf.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✓ Saved CDF plot: {output_path}{Colors.ENDC}")
    
    def plot_boxplot_comparison(self, output_dir='visualizations'):
        """Generate side-by-side boxplot comparing GET vs PUT latencies"""
        if not any(self.latencies.values()):
            print(f"\n{Colors.WARNING}⚠ No latency data available for plotting{Colors.ENDC}")
            return
        
        Path(output_dir).mkdir(exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data for boxplot
        data_to_plot = []
        labels = []
        colors_list = []
        
        for op_type in ['GET', 'PUT']:
            if op_type in self.latencies and self.latencies[op_type]:
                data_to_plot.append(self.latencies[op_type])
                labels.append(f'{op_type}\n(n={len(self.latencies[op_type])})')
                colors_list.append('#4ECDC4' if op_type == 'GET' else '#FF6B6B')
        
        if not data_to_plot:
            print(f"\n{Colors.WARNING}⚠ No data available for boxplot{Colors.ENDC}")
            return
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True, 
                       showmeans=True, meanline=False,
                       medianprops=dict(color='black', linewidth=2),
                       meanprops=dict(marker='D', markerfacecolor='yellow', markeredgecolor='black', markersize=8))
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
        ax.set_title('GET vs PUT Latency Comparison', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add legend for mean/median
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='black', linewidth=2, label='Median'),
            Line2D([0], [0], marker='D', color='w', markerfacecolor='yellow', 
                  markeredgecolor='black', markersize=8, label='Mean')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        output_path = Path(output_dir) / 'latency_boxplot_comparison.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✓ Saved boxplot comparison: {output_path}{Colors.ENDC}")
    
    def plot_throughput_histogram(self, output_dir='visualizations', window_size=1):
        """Generate throughput histogram showing operations per time window"""
        if len(self.timestamps) < 2:
            print(f"\n{Colors.WARNING}⚠ Not enough data for throughput histogram{Colors.ENDC}")
            return
        
        Path(output_dir).mkdir(exist_ok=True)
        
        # Sort operations by timestamp
        sorted_ops = sorted(self.operations, key=lambda x: x[0])
        
        # Create time windows
        start_time = sorted_ops[0][0]
        end_time = sorted_ops[-1][0]
        time_span = (end_time - start_time).total_seconds()
        
        if time_span <= 0:
            print(f"\n{Colors.WARNING}⚠ All operations occurred at the same time{Colors.ENDC}")
            return
        
        # Calculate throughput per window
        num_windows = max(1, int(time_span / window_size))
        throughput_data = {'PUT': [0] * num_windows, 'GET': [0] * num_windows}
        
        for timestamp, op_type, status in sorted_ops:
            elapsed = (timestamp - start_time).total_seconds()
            window_idx = min(int(elapsed / window_size), num_windows - 1)
            throughput_data[op_type][window_idx] += 1
        
        # Convert to operations per second
        for op_type in throughput_data:
            throughput_data[op_type] = [count / window_size for count in throughput_data[op_type]]
        
        # Plot
        fig, ax = plt.subplots(figsize=(14, 6))
        
        x = np.arange(num_windows) * window_size
        width = window_size * 0.4
        
        colors = {'PUT': '#FF6B6B', 'GET': '#4ECDC4'}
        ax.bar(x - width/2, throughput_data['PUT'], width, label='PUT', 
              color=colors['PUT'], alpha=0.7, edgecolor='black', linewidth=0.5)
        ax.bar(x + width/2, throughput_data['GET'], width, label='GET', 
              color=colors['GET'], alpha=0.7, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel(f'Time (seconds from start)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Throughput (ops/sec)', fontsize=12, fontweight='bold')
        ax.set_title(f'Throughput Over Time (window={window_size}s)', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        output_path = Path(output_dir) / 'throughput_histogram.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✓ Saved throughput histogram: {output_path}{Colors.ENDC}")
    
    # Replace the entire plot_throughput_boxplot_comparison method with:

    def plot_throughput_boxplot_comparison(self, output_dir='visualizations', window_size=1):
        """Generate boxplot comparing GET vs PUT throughput distributions"""
        if len(self.timestamps) < 2:
            print(f"\n{Colors.WARNING}⚠ Not enough data for throughput boxplot{Colors.ENDC}")
            return
        
        Path(output_dir).mkdir(exist_ok=True)
        
        # Sort operations by timestamp
        sorted_ops = sorted(self.operations, key=lambda x: x[0])
        
        start_time = sorted_ops[0][0]
        end_time = sorted_ops[-1][0]
        time_span = (end_time - start_time).total_seconds()
        
        if time_span <= 0:
            print(f"\n{Colors.WARNING}⚠ All operations occurred at the same time{Colors.ENDC}")
            return
        
        # Calculate throughput per window for each operation type
        num_windows = max(1, int(time_span / window_size))
        throughput_put = []
        throughput_get = []
        
        for i in range(num_windows):
            window_start = start_time.timestamp() + i * window_size
            window_end = window_start + window_size
            
            put_count = sum(1 for ts, op, _ in sorted_ops 
                        if window_start <= ts.timestamp() < window_end and op == 'PUT')
            get_count = sum(1 for ts, op, _ in sorted_ops 
                        if window_start <= ts.timestamp() < window_end and op == 'GET')
            
            if put_count > 0:
                throughput_put.append(put_count / window_size)
            if get_count > 0:
                throughput_get.append(get_count / window_size)
        
        if not throughput_put and not throughput_get:
            print(f"\n{Colors.WARNING}⚠ No throughput data to plot{Colors.ENDC}")
            return
        
        # Create side-by-side subplots with independent y-axes
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot GET
        if throughput_get:
            bp_get = axes[0].boxplot([throughput_get], labels=[f'GET\n({len(throughput_get)} windows)'], 
                                    patch_artist=True, showmeans=True, meanline=False, widths=0.6,
                                    medianprops=dict(color='black', linewidth=2),
                                    meanprops=dict(marker='D', markerfacecolor='yellow', 
                                                markeredgecolor='black', markersize=10))
            bp_get['boxes'][0].set_facecolor('#4ECDC4')
            bp_get['boxes'][0].set_alpha(0.7)
            
            axes[0].set_ylabel('Throughput (ops/sec)', fontsize=12, fontweight='bold')
            axes[0].set_title('GET Throughput', fontsize=13, fontweight='bold')
            axes[0].grid(True, alpha=0.3, axis='y')
            
            # Add statistics text
            get_stats = f"Mean: {np.mean(throughput_get):.2f}\nMedian: {np.median(throughput_get):.2f}\nStd: {np.std(throughput_get):.2f}"
            axes[0].text(0.98, 0.98, get_stats, transform=axes[0].transAxes,
                        fontsize=10, verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Plot PUT
        if throughput_put:
            bp_put = axes[1].boxplot([throughput_put], labels=[f'PUT\n({len(throughput_put)} windows)'], 
                                    patch_artist=True, showmeans=True, meanline=False, widths=0.6,
                                    medianprops=dict(color='black', linewidth=2),
                                    meanprops=dict(marker='D', markerfacecolor='yellow', 
                                                markeredgecolor='black', markersize=10))
            bp_put['boxes'][0].set_facecolor('#FF6B6B')
            bp_put['boxes'][0].set_alpha(0.7)
            
            axes[1].set_ylabel('Throughput (ops/sec)', fontsize=12, fontweight='bold')
            axes[1].set_title('PUT Throughput', fontsize=13, fontweight='bold')
            axes[1].grid(True, alpha=0.3, axis='y')
            
            # Add statistics text
            put_stats = f"Mean: {np.mean(throughput_put):.2f}\nMedian: {np.median(throughput_put):.2f}\nStd: {np.std(throughput_put):.2f}"
            axes[1].text(0.98, 0.98, put_stats, transform=axes[1].transAxes,
                        fontsize=10, verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
        
        # Add shared legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='black', linewidth=2, label='Median'),
            Line2D([0], [0], marker='D', color='w', markerfacecolor='yellow', 
                markeredgecolor='black', markersize=10, label='Mean')
        ]
        fig.legend(handles=legend_elements, loc='upper center', ncol=2, 
                fontsize=11, bbox_to_anchor=(0.5, 0.98))
        
        fig.suptitle(f'GET vs PUT Throughput Comparison (window={window_size}s)', 
                    fontsize=14, fontweight='bold', y=0.93)
        
        output_path = Path(output_dir) / 'throughput_boxplot_comparison.png'
        plt.tight_layout(rect=[0, 0, 1, 0.91])
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✓ Saved throughput boxplot: {output_path}{Colors.ENDC}")
    
    def plot_stacked_throughput(self, output_dir='visualizations', window_size=1):
        """Generate stacked area chart showing GET/PUT throughput breakdown"""
        if len(self.timestamps) < 2:
            print(f"\n{Colors.WARNING}⚠ Not enough data for stacked throughput{Colors.ENDC}")
            return
        
        Path(output_dir).mkdir(exist_ok=True)
        
        # Sort operations by timestamp
        sorted_ops = sorted(self.operations, key=lambda x: x[0])
        
        start_time = sorted_ops[0][0]
        end_time = sorted_ops[-1][0]
        time_span = (end_time - start_time).total_seconds()
        
        if time_span <= 0:
            print(f"\n{Colors.WARNING}⚠ All operations occurred at the same time{Colors.ENDC}")
            return
        
        # Create time windows
        num_windows = max(1, int(time_span / window_size))
        time_points = []
        throughput_put = []
        throughput_get = []
        
        for i in range(num_windows):
            window_start = start_time.timestamp() + i * window_size
            window_end = window_start + window_size
            
            put_count = sum(1 for ts, op, _ in sorted_ops 
                          if window_start <= ts.timestamp() < window_end and op == 'PUT')
            get_count = sum(1 for ts, op, _ in sorted_ops 
                          if window_start <= ts.timestamp() < window_end and op == 'GET')
            
            time_points.append(datetime.fromtimestamp(start_time.timestamp() + i * window_size))
            throughput_put.append(put_count / window_size)
            throughput_get.append(get_count / window_size)
        
        # Plot
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.fill_between(time_points, 0, throughput_get, 
                       label='GET', color='#4ECDC4', alpha=0.7)
        ax.fill_between(time_points, throughput_get, 
                       [g + p for g, p in zip(throughput_get, throughput_put)],
                       label='PUT', color='#FF6B6B', alpha=0.7)
        
        # Add total line on top
        total = [g + p for g, p in zip(throughput_get, throughput_put)]
        ax.plot(time_points, total, color='black', linewidth=2, 
               linestyle='--', label='Total', alpha=0.8)
        
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.set_ylabel('Throughput (ops/sec)', fontsize=12, fontweight='bold')
        ax.set_title(f'Stacked Throughput: GET + PUT (window={window_size}s)', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Format x-axis
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)
        
        output_path = Path(output_dir) / 'throughput_stacked.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✓ Saved stacked throughput chart: {output_path}{Colors.ENDC}")
    
    def run(self):
        """Main analysis workflow"""
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.OKBLUE}  Performance Analysis from Log Files{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.OKBLUE}{'='*60}{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Log Directory:{Colors.ENDC} {self.log_dir.absolute()}")
        
        # Try client logs first (more accurate)
        found_data = self.parse_client_logs()
        
        # Fallback to worker logs if needed
        if not found_data:
            print(f"\n{Colors.WARNING}Falling back to worker log analysis...{Colors.ENDC}")
            found_data = self.parse_worker_logs()
        
        if not found_data:
            print(f"\n{Colors.FAIL}❌ No performance data found in logs{Colors.ENDC}")
            print(f"\n{Colors.WARNING}Suggestions:{Colors.ENDC}")
            print("  1. Make sure you've run some operations (PUT/GET)")
            print("  2. Check that logs exist in the specified directory")
            print("  3. Verify the log format matches expected patterns")
            return
        
        # Calculate and display statistics
        for op_type in ['PUT', 'GET']:
            if op_type in self.latencies and self.latencies[op_type]:
                self.calculate_statistics(self.latencies[op_type], op_type)
        
        # Overall statistics
        all_latencies = []
        for latency_list in self.latencies.values():
            all_latencies.extend(latency_list)
        
        if all_latencies:
            self.calculate_statistics(all_latencies, "Overall")
        
        # Throughput analysis
        self.calculate_throughput()
        
        # Generate visualizations
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}  Generating Visualizations{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        self.plot_latency_distribution()
        self.plot_cdf()
        self.plot_boxplot_comparison()
        self.plot_throughput_histogram()
        self.plot_throughput_boxplot_comparison()
        self.plot_stacked_throughput()
        
        print(f"\n{Colors.OKGREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Analysis Complete!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'='*60}{Colors.ENDC}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze latency and throughput from log files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--log-dir',
        default='logs',
        help='Directory containing log files (default: logs)'
    )
    
    args = parser.parse_args()
    
    analyzer = LatencyAnalyzer(log_dir="../logs")
    analyzer.run()


if __name__ == '__main__':
    main()