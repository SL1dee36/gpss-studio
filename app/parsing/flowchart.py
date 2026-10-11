import re

from app.consts import GPSS_FLOWCHART_BLOCKS


class GPSSFlowchartParser:
    @classmethod
    def parse(cls, code_text):
        lines = code_text.splitlines()
        blocks = []
        labels = {}

        for idx, line in enumerate(lines):
            line_no = idx + 1
            clean = line.strip()
            if not clean or clean.startswith('*'):
                continue

            comment = ''
            if ';' in clean:
                clean, comment = clean.split(';', 1)
                clean = clean.strip()
                comment = ';' + comment.strip()

            tokens = clean.split()
            if not tokens:
                continue

            label = ''
            first = tokens[0].upper().rstrip(':')

            if first in GPSS_FLOWCHART_BLOCKS:
                op = first
                arg_tokens = tokens[1:]
            elif len(tokens) > 1 and tokens[1].upper().rstrip(':') in GPSS_FLOWCHART_BLOCKS:
                label = tokens[0].rstrip(':')
                op = tokens[1].upper().rstrip(':')
                arg_tokens = tokens[2:]
            else:
                continue  # Пропускаем SIMULATE, START, END, STORAGE, TABLE и другие не-блоки

            # Поддержка составных условий: TEST L, TEST GE, GATE NU и т.д.
            aux_candidates = {
                "TEST": {"L", "LE", "E", "NE", "G", "GE"},
                "GATE": {"LS", "LR", "U", "NU", "SF", "SNF", "SE", "SNE", "NI", "I"},
                "LOGIC": {"S", "R", "I"},
                "SELECT": {"L", "LE", "E", "NE", "G", "GE", "MIN", "MAX"}
            }
            if op in aux_candidates and arg_tokens and arg_tokens[0].upper() in aux_candidates[op]:
                op = f"{op} {arg_tokens[0].upper()}"
                arg_tokens = arg_tokens[1:]

            operands = " ".join(arg_tokens)

            b_idx = len(blocks)
            if label:
                labels[label.upper()] = b_idx

            blocks.append({
                'index': b_idx,
                'block_num': b_idx + 1,
                'line_no': line_no,
                'label': label,
                'op': op,
                'operands': operands,
                'comment': comment,
                'total': '0',
                'current': '0'
            })

        edges = []
        for i, b in enumerate(blocks):
            base_op = b['op'].split()[0]
            raw_ops = [p.strip() for p in b['operands'].split(',')] if b['operands'] else []

            if base_op == 'TERMINATE':
                continue
            elif base_op == 'TRANSFER':
                if len(raw_ops) >= 2 and raw_ops[0] == '':
                    # Безусловный переход TRANSFER ,LABEL
                    target = raw_ops[1].upper()
                    edges.append({
                        'from': i, 'to': labels.get(target, None),
                        'target_label': target, 'type': 'jump', 'label': ''
                    })
                elif len(raw_ops) >= 2 and re.match(r'^(\d*\.\d+|\d+)$', raw_ops[0]):
                    # Статистический переход TRANSFER p,B,C
                    prob = float(raw_ops[0])
                    t_b = raw_ops[1].upper() if raw_ops[1] else ''
                    t_c = raw_ops[2].upper() if len(raw_ops) > 2 and raw_ops[2] else ''

                    p_c_label = f"{round(prob * 100)}%"
                    p_b_label = f"{round((1 - prob) * 100)}%"

                    # Ветка B (1-p)
                    b_idx = labels.get(t_b, i + 1 if not t_b else None)
                    edges.append({
                        'from': i, 'to': b_idx,
                        'target_label': t_b or 'next', 'type': 'prob', 'label': p_b_label
                    })
                    # Ветка C (p)
                    c_idx = labels.get(t_c, i + 1 if not t_c else None)
                    edges.append({
                        'from': i, 'to': c_idx,
                        'target_label': t_c or 'next', 'type': 'prob', 'label': p_c_label
                    })
                elif len(raw_ops) >= 2 and raw_ops[0].upper() in ('BOTH', 'ALL'):
                    for sub_t in raw_ops[1:]:
                        st = sub_t.upper()
                        edges.append({
                            'from': i, 'to': labels.get(st, None),
                            'target_label': st, 'type': 'both', 'label': raw_ops[0].lower()
                        })
                else:
                    if raw_ops and raw_ops[0].upper() in labels:
                        st = raw_ops[0].upper()
                        edges.append({
                            'from': i, 'to': labels.get(st, None),
                            'target_label': st, 'type': 'jump', 'label': ''
                        })
                    elif i + 1 < len(blocks):
                        edges.append({'from': i, 'to': i + 1, 'target_label': '', 'type': 'seq', 'label': ''})
            elif base_op in ('TEST', 'GATE', 'LOOP'):
                target = raw_ops[-1].upper() if raw_ops else ''
                if target in labels:
                    edges.append({
                        'from': i, 'to': labels[target],
                        'target_label': target, 'type': 'branch', 'label': 'ветвь'
                    })
                if i + 1 < len(blocks):
                    edges.append({'from': i, 'to': i + 1, 'target_label': '', 'type': 'seq', 'label': ''})
            elif base_op == 'SPLIT':
                target = raw_ops[1].upper() if len(raw_ops) > 1 else ''
                if target in labels:
                    edges.append({
                        'from': i, 'to': labels[target],
                        'target_label': target, 'type': 'split', 'label': 'копия'
                    })
                if i + 1 < len(blocks):
                    edges.append({'from': i, 'to': i + 1, 'target_label': '', 'type': 'seq', 'label': ''})
            else:
                if i + 1 < len(blocks):
                    edges.append({'from': i, 'to': i + 1, 'target_label': '', 'type': 'seq', 'label': ''})

        # Сегментация: новая колонка создается ТОЛЬКО для нового GENERATE или после разрыва потока (не по каждой метке!)
        segments = []
        current_seg = None
        gen_count = 0
        for i, b in enumerate(blocks):
            base_op = b['op'].split()[0]
            starts_new = False

            if base_op == 'GENERATE':
                starts_new = True
                gen_count += 1
            elif i > 0:
                prev_op = blocks[i - 1]['op'].split()[0]
                prev_has_fallthrough = any(e['from'] == i - 1 and e['to'] == i for e in edges)
                if prev_op in ('TERMINATE', 'TRANSFER') and not prev_has_fallthrough:
                    starts_new = True

            if starts_new or current_seg is None:
                if base_op == 'GENERATE':
                    title = f"Поток #{gen_count}" + (f" [{b['label']}]" if b['label'] else "")
                elif b['label']:
                    title = f"Подпрограмма [{b['label']}]"
                else:
                    title = f"Сегмент #{len(segments) + 1}"

                current_seg = {
                    'id': len(segments),
                    'title': title,
                    'block_indices': []
                }
                segments.append(current_seg)

            current_seg['block_indices'].append(i)

        return blocks, edges, segments, labels
