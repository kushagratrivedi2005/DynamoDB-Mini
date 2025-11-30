
import re
from datetime import datetime

def analyze_logs(log_file_path='../logs/client.log'):
    """
    Analyzes the client log file to calculate latency and throughput.

    Args:
        log_file_path (str): The path to the client log file.
    """
    latencies = []
    requests = {}
    successful_ops = 0
    first_timestamp = None
    last_timestamp = None

    # Regex to capture timestamp, log level, message type, and key-value pairs
    log_pattern = re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (?P<level>\w+) - "
        r"\[(?P<type>LATENCY_START|LATENCY_END)\] "
        r"(?P<data>.*)$"
    )
    
    data_pattern = re.compile(r"(\w+)=([\w-]+)")

    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                match = log_pattern.match(line.strip())
                if not match:
                    continue

                log_data = match.groupdict()
                timestamp = datetime.strptime(log_data['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                
                if first_timestamp is None:
                    first_timestamp = timestamp
                last_timestamp = timestamp

                data_pairs = dict(data_pattern.findall(log_data['data']))
                request_id = data_pairs.get('request_id')

                if not request_id:
                    continue

                if log_data['type'] == 'LATENCY_START':
                    requests[request_id] = {'start_time': timestamp}
                elif log_data['type'] == 'LATENCY_END':
                    if request_id in requests and 'start_time' in requests[request_id]:
                        start_time = requests[request_id]['start_time']
                        latency = (timestamp - start_time).total_seconds() * 1000  # in milliseconds
                        latencies.append(latency)
                        
                        if data_pairs.get('status') == 'SUCCESS':
                            successful_ops += 1
                        
                        # Clean up completed request
                        del requests[request_id]

    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_file_path}'")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    if not latencies:
        print("No completed requests found in the log file to analyze.")
        return

    # --- Calculations ---
    avg_latency = sum(latencies) / len(latencies)
    
    total_time_seconds = (last_timestamp - first_timestamp).total_seconds() if first_timestamp and last_timestamp else 0
    throughput = successful_ops / total_time_seconds if total_time_seconds > 0 else 0

    # --- Output ---
    print("\n--- Performance Analysis ---")
    print(f"Total requests analyzed: {len(latencies)}")
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"Throughput: {throughput:.2f} ops/sec")
    print("--------------------------\n")


if __name__ == "__main__":
    # The default path is relative to the `test` directory
    analyze_logs()
