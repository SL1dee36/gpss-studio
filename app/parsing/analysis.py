import re


def analyze_device_grouping(parser, code_text):
    if not parser:
        return [], {}

    q_map = {}
    lines = [l.strip() for l in code_text.splitlines() if l.strip() and not l.strip().startswith('*')]
    for i, line in enumerate(lines):
        m_q = re.search(r'\bQUEUE\s+([A-Za-z0-9_$#]+)', line, re.IGNORECASE)
        if m_q:
            q_name = m_q.group(1).upper()
            for j in range(i+1, min(i+6, len(lines))):
                m_s = re.search(r'\b(SEIZE|ENTER)\s+([A-Za-z0-9_$#]+)', lines[j], re.IGNORECASE)
                if m_s:
                    dev_name = m_s.group(2).upper()
                    q_map[dev_name] = q_name
                    break

    queues_by_name = {q['name'].upper(): q for q in parser.queues}

    grouped_devices = []
    utils_list = []
    total_entries_count = 0

    for f in parser.facilities:
        fn = f['name'].upper()
        qn = q_map.get(fn, '')
        if not qn:
            for k in queues_by_name:
                if k.endswith(fn) or fn.endswith(k) or (re.sub(r'\D', '', k) == re.sub(r'\D', '', fn) and re.sub(r'\D', '', fn)):
                    qn = k
                    break
        q_info = queues_by_name.get(qn, {})

        try:
            t_serv = float(f['avg_time'])
        except Exception:
            t_serv = 0.0
        try:
            t_wait = float(q_info.get('avg_t', 0.0))
        except Exception:
            t_wait = 0.0
        t_total = t_serv + t_wait

        try:
            u_val = float(f['util'])
            utils_list.append((f['name'], u_val))
        except Exception:
            u_val = 0.0

        try:
            e_cnt = int(f['entries'])
            total_entries_count += e_cnt
        except Exception:
            pass

        pct_z = q_info.get('pct_z', '')
        grouped_devices.append({
            'device': f['name'],
            'type': 'Одноканальный',
            'util': f['util'],
            'util_val': u_val,
            'entries': f['entries'],
            'avg_serv': f['avg_time'],
            'avg_serv_val': t_serv,
            'queue': qn or '-',
            'q_avg_len': q_info.get('avg_c', '-'),
            'q_max_len': q_info.get('max_c', '-'),
            'q_avg_wait': q_info.get('avg_t', '-'),
            'q_avg_wait_val': t_wait,
            'q_zero_pct': f"{pct_z}%" if pct_z else '-',
            'total_node_time': f"{t_total:.3f}" if q_info else f['avg_time'],
            'total_node_val': t_total if q_info else t_serv,
            'status': f['status'],
            'line_no': f['line_no'],
            'q_line_no': q_info.get('line_no', f['line_no'])
        })

    for s in parser.storages:
        sn = s['name'].upper()
        qn = q_map.get(sn, '')
        q_info = queues_by_name.get(qn, {})

        try:
            t_serv = float(s['avg_time'])
        except Exception:
            t_serv = 0.0
        try:
            t_wait = float(q_info.get('avg_t', 0.0))
        except Exception:
            t_wait = 0.0
        t_total = t_serv + t_wait

        try:
            u_val = float(s['util'])
            utils_list.append((s['name'], u_val))
        except Exception:
            u_val = 0.0

        pct_z = q_info.get('pct_z', '')
        grouped_devices.append({
            'device': s['name'],
            'type': 'Многоканальный',
            'util': s['util'],
            'util_val': u_val,
            'entries': s['entries'],
            'avg_serv': s['avg_time'],
            'avg_serv_val': t_serv,
            'queue': qn or '-',
            'q_avg_len': q_info.get('avg_c', '-'),
            'q_max_len': q_info.get('max_c', '-'),
            'q_avg_wait': q_info.get('avg_t', '-'),
            'q_avg_wait_val': t_wait,
            'q_zero_pct': f"{pct_z}%" if pct_z else '-',
            'total_node_time': f"{t_total:.3f}" if q_info else s['avg_time'],
            'total_node_val': t_total if q_info else t_serv,
            'status': s['status'],
            'line_no': s['line_no'],
            'q_line_no': q_info.get('line_no', s['line_no'])
        })

    mean_u = sum(u for _, u in utils_list) / len(utils_list) if utils_list else 0.0
    bottleneck_dev, max_u = max(utils_list, key=lambda x: x[1]) if utils_list else ("-", 0.0)

    worst_q = "-"
    max_q_val = 0.0
    for q in parser.queues:
        try:
            v = float(q['max_c'])
            if v > max_q_val:
                max_q_val = v
                worst_q = q['name']
        except Exception:
            pass

    summary = {
        'total_devices': len(grouped_devices),
        'mean_util': mean_u,
        'bottleneck_device': bottleneck_dev,
        'bottleneck_util': max_u,
        'worst_queue': worst_q,
        'max_q_len': max_q_val,
        'total_entries': total_entries_count
    }

    return grouped_devices, summary


