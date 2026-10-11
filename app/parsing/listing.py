import re


class GPSSListingParser:
    def __init__(self, text):
        self.text = text
        self.lines = text.replace("\r\n", "\n").split("\n")
        self.header_info = {}
        self.clocks = {}
        self.model_size = {}
        self.storage_requirements = {}
        self.common_storage = {}
        self.execution_stats = {}
        self.elapsed_time = {}
        self.facilities = []
        self.queues = []
        self.storages = []
        self.blocks = []
        self.random_streams = []
        self.parse()

    def parse(self):
        state = None
        block_col_pos = []

        for idx, line in enumerate(self.lines):
            line_no = idx + 1
            s = line.strip()

            if "GPSS/H Release" in line and not self.header_info:
                m_ver = re.search(r"GPSS/H\s+Release\s+([^\s]+(?:\s*\([^\)]+\))?)", line)
                ver = m_ver.group(1) if m_ver else "GPSS/H"
                m_file = re.search(r"File:\s*([^\s]+)", line)
                f_name = m_file.group(1) if m_file else ""
                self.header_info = {"version": ver, "file": f_name, "line_no": line_no}

            if "Relative Clock:" in line:
                m_rel = re.search(r"Relative Clock:\s*([\d\.]+)", line)
                m_abs = re.search(r"Absolute Clock:\s*([\d\.]+)", line)
                self.clocks["relative"] = m_rel.group(1) if m_rel else "0.0"
                self.clocks["absolute"] = m_abs.group(1) if m_abs else "0.0"
                self.clocks["line_no"] = line_no

            if "Simulation complete." in line:
                m_abs = re.search(r"Absolute Clock:\s*([\d\.]+)", line)
                if m_abs:
                    self.clocks["absolute"] = m_abs.group(1)
                    if "line_no" not in self.clocks:
                        self.clocks["line_no"] = line_no

            if "Total Block Executions:" in line:
                m = re.search(r"Total Block Executions:\s*(\d+)", line)
                if m:
                    self.execution_stats["total_blocks"] = m.group(1)
                    self.execution_stats["line_no"] = line_no
            if "Blocks / second:" in line:
                m = re.search(r"Blocks\s*/\s*second:\s*([\d\.]+)", line)
                if m:
                    self.execution_stats["blocks_per_sec"] = m.group(1)
            if "Microseconds / Block:" in line:
                m = re.search(r"Microseconds\s*/\s*Block:\s*([\d\.]+)", line)
                if m:
                    self.execution_stats["us_per_block"] = m.group(1)

            if "Control Statements" in line and "Blocks" not in line:
                m = re.search(r"Control Statements\s+(\d+)", line)
                if m:
                    self.model_size["control_statements"] = m.group(1)
                    self.model_size["line_no"] = line_no
            if re.match(r"^\s*Blocks\s+\d+", line):
                m = re.search(r"Blocks\s+(\d+)", line)
                if m:
                    self.model_size["blocks"] = m.group(1)
                    if "line_no" not in self.model_size:
                        self.model_size["line_no"] = line_no

            if "Compiled Code:" in line:
                m = re.search(r"Compiled Code:\s*(\d+)", line)
                if m:
                    self.storage_requirements["compiled_code"] = m.group(1)
                    self.storage_requirements["line_no"] = line_no
            if "Compiled Data:" in line:
                m = re.search(r"Compiled Data:\s*(\d+)", line)
                if m:
                    self.storage_requirements["compiled_data"] = m.group(1)
            if "Entities:" in line and "Dictionary" not in line:
                m = re.search(r"Entities:\s*(\d+)", line)
                if m:
                    self.storage_requirements["entities"] = m.group(1)
            if "Common:" in line:
                m = re.search(r"Common:\s*(\d+)", line)
                if m:
                    self.storage_requirements["common"] = m.group(1)
            if re.match(r"^\s*Total:\s*\d+", line):
                m = re.search(r"Total:\s*(\d+)", line)
                if m:
                    self.storage_requirements["total"] = m.group(1)

            if "bytes available" in line:
                m = re.search(r"(\d+)\s+bytes available", line)
                if m:
                    self.common_storage["available"] = m.group(1)
                    self.common_storage["line_no"] = line_no
            if "in use" in line:
                m = re.search(r"(\d+)\s+in use", line)
                if m:
                    self.common_storage["in_use"] = m.group(1)
            if "used (max)" in line:
                m = re.search(r"(\d+)\s+used \(max\)", line)
                if m:
                    self.common_storage["max_used"] = m.group(1)

            if "Facility" in line and ("Total" in line or "Avail" in line):
                state = "facility_hdr"
                continue
            if state == "facility_hdr":
                if "Time" in line or "Status" in line:
                    state = "facilities"
                    continue
                state = None

            if state == "facilities":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Queue", "Storage", "Random", "Status of", "Relative Clock", "Simulation"]):
                    state = None
                else:
                    name = line[0:10].strip()
                    if name and not name.startswith("-"):
                        self.facilities.append({
                            "line_no": line_no,
                            "name": name,
                            "util": line[10:17].strip() if len(line) > 10 else "",
                            "avail_util": line[17:24].strip() if len(line) > 17 else "",
                            "unavl_util": line[24:31].strip() if len(line) > 24 else "",
                            "entries": line[31:43].strip() if len(line) > 31 else "",
                            "avg_time": line[43:56].strip() if len(line) > 43 else "",
                            "status": line[56:66].strip() if len(line) > 56 else "",
                            "pct_avail": line[66:75].strip() if len(line) > 66 else "",
                            "seizing": line[75:85].strip() if len(line) > 75 else "",
                            "preempting": line[85:95].strip() if len(line) > 85 else ""
                        })

            if "Queue" in line and ("Maximum" in line or "Average" in line):
                state = "queue_hdr"
                continue
            if state == "queue_hdr":
                if "Contents" in line or "Entries" in line:
                    state = "queues"
                    continue
                state = None

            if state == "queues":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Facility", "Storage", "Random", "Status of", "Relative Clock", "Simulation"]):
                    state = None
                else:
                    name = line[0:10].strip()
                    if name and not name.startswith("-"):
                        self.queues.append({
                            "line_no": line_no,
                            "name": name,
                            "max_c": line[10:21].strip() if len(line) > 10 else "",
                            "avg_c": line[21:34].strip() if len(line) > 21 else "",
                            "total_e": line[34:47].strip() if len(line) > 34 else "",
                            "zero_e": line[47:58].strip() if len(line) > 47 else "",
                            "pct_z": line[58:69].strip() if len(line) > 58 else "",
                            "avg_t": line[69:83].strip() if len(line) > 69 else "",
                            "dollar_avg_t": line[83:97].strip() if len(line) > 83 else "",
                            "qtable": line[97:107].strip() if len(line) > 97 else "",
                            "cur_c": line[107:].strip() if len(line) > 107 else ""
                        })

            if "Storage" in line and ("Capacity" in line or "Average" in line or "Avg-Util" in line):
                state = "storage_hdr"
                continue
            if state == "storage_hdr":
                if "Contents" in line or "Time" in line or "Status" in line:
                    state = "storages"
                    continue
                state = None

            if state == "storages":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Facility", "Queue", "Random", "Status of", "Relative Clock", "Simulation"]):
                    state = None
                else:
                    name = line[0:10].strip()
                    if name and not name.startswith("-"):
                        self.storages.append({
                            "line_no": line_no,
                            "name": name,
                            "util": line[10:17].strip() if len(line) > 10 else "",
                            "avail_util": line[17:24].strip() if len(line) > 17 else "",
                            "unavl_util": line[24:31].strip() if len(line) > 24 else "",
                            "entries": line[31:43].strip() if len(line) > 31 else "",
                            "avg_time": line[43:56].strip() if len(line) > 43 else "",
                            "status": line[56:66].strip() if len(line) > 56 else "",
                            "pct_avail": line[66:76].strip() if len(line) > 66 else "",
                            "capacity": line[76:88].strip() if len(line) > 76 else "",
                            "avg_contents": line[88:100].strip() if len(line) > 88 else "",
                            "cur_contents": line[100:112].strip() if len(line) > 100 else "",
                            "max_contents": line[112:].strip() if len(line) > 112 else ""
                        })

            if "Block Current     Total" in line:
                state = "blocks"
                block_col_pos = [m.start() for m in re.finditer(r"Block", line)]
                continue
            if state == "blocks":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Facility", "Storage", "Queue", "Random", "Status of", "Relative Clock", "Simulation"]):
                    state = None
                else:
                    for p in block_col_pos:
                        chunk = line[p:p+25]
                        if not chunk.strip():
                            continue
                        blk = chunk[:12].strip()
                        if not blk or blk == "Block":
                            continue
                        cur = chunk[12:18].strip() or "0"
                        tot = chunk[18:].strip()
                        self.blocks.append({
                            "line_no": line_no,
                            "block": blk,
                            "current": cur,
                            "total": tot
                        })

            if "Random    Antithetic" in line:
                state = "random_hdr"
                continue
            if state == "random_hdr":
                if "Stream" in line or "Variates" in line:
                    state = "random"
                    continue
                state = None
            if state == "random":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Status of", "Simulation", "Facility", "Queue", "Storage"]):
                    state = None
                else:
                    parts = line.split()
                    if len(parts) >= 5:
                        self.random_streams.append({
                            "line_no": line_no,
                            "stream": parts[0],
                            "antithetic": parts[1],
                            "initial_pos": parts[2],
                            "current_pos": parts[3],
                            "sample_count": parts[4],
                            "chi_square": parts[5] if len(parts) > 5 else "N/A"
                        })
