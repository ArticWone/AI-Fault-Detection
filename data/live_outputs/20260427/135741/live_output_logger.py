import csv
import time
from datetime import datetime
from pathlib import Path
from pymodbus.client import ModbusTcpClient

HOST = 'MACHINE_IP'
UNIT = 1
POLL_SECONDS = 2.0
CHUNK = 50
RANGES = [(10000, 250), (10100, 250), (13300, 300), (13400, 300), (13500, 300)]
FUNCTIONS = [('holding', 'read_holding_registers'), ('input', 'read_input_registers')]
OUT_DIR = Path(__file__).resolve().parent
SAMPLES = OUT_DIR / 'live_outputs.csv'
CHANGES = OUT_DIR / 'changes.csv'
RUN_LOG = OUT_DIR / 'run.log'

sample_fields = ['timestamp','cycle','function','address','value','status','error']
change_fields = ['timestamp','cycle','function','address','previous_value','value']
previous = {}

def emit(message):
    line = f"{datetime.now().isoformat(timespec='seconds')} {message}"
    print(line, flush=True)
    with RUN_LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')

def ensure_header(path, fields):
    if not path.exists() or path.stat().st_size == 0:
        with path.open('w', newline='', encoding='utf-8') as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()

def read_blocks(client, kind, fn_name):
    fn = getattr(client, fn_name)
    for start, count in RANGES:
        for address in range(start, start + count, CHUNK):
            size = min(CHUNK, start + count - address)
            try:
                response = fn(address, count=size, device_id=UNIT)
                if response.isError():
                    yield address, None, 'error', str(response)
                    continue
                for offset, value in enumerate(response.registers):
                    yield address + offset, int(value), 'ok', ''
            except Exception as exc:
                yield address, None, 'error', repr(exc)

ensure_header(SAMPLES, sample_fields)
ensure_header(CHANGES, change_fields)
emit(f'Live output logger starting host={HOST} unit={UNIT} poll={POLL_SECONDS}s ranges={RANGES}')

client = ModbusTcpClient(HOST, port=502, timeout=1)
while not client.connect():
    emit('Waiting for Modbus TCP endpoint')
    time.sleep(2)

emit('Modbus TCP connection established')
cycle = 0
try:
    while True:
        cycle += 1
        ts = datetime.now().isoformat(timespec='milliseconds')
        ok_count = 0
        changed_count = 0
        with SAMPLES.open('a', newline='', encoding='utf-8') as sf, CHANGES.open('a', newline='', encoding='utf-8') as cf:
            sample_writer = csv.DictWriter(sf, fieldnames=sample_fields)
            change_writer = csv.DictWriter(cf, fieldnames=change_fields)
            for kind, fn_name in FUNCTIONS:
                for address, value, status, error in read_blocks(client, kind, fn_name):
                    if status == 'ok':
                        ok_count += 1
                    sample_writer.writerow({
                        'timestamp': ts,
                        'cycle': cycle,
                        'function': kind,
                        'address': address,
                        'value': '' if value is None else value,
                        'status': status,
                        'error': error,
                    })
                    key = (kind, address)
                    if status == 'ok' and key in previous and previous[key] != value:
                        changed_count += 1
                        change_writer.writerow({
                            'timestamp': ts,
                            'cycle': cycle,
                            'function': kind,
                            'address': address,
                            'previous_value': previous[key],
                            'value': value,
                        })
                    if status == 'ok':
                        previous[key] = value
        emit(f'cycle={cycle} ok_values={ok_count} changed={changed_count}')
        time.sleep(POLL_SECONDS)
except KeyboardInterrupt:
    emit('Ctrl+C received; stopping')
finally:
    client.close()
    emit('Modbus connection closed')
