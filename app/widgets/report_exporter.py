import datetime
import html
import os
import webbrowser
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QMessageBox


class ReportExporter:
    @staticmethod
    def generate_html(model_name, code, parser, theme="light"):
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        safe_model_name = html.escape(model_name or "Новая модель")
        escaped_code = html.escape(code or "")

        # Форматирование исходного кода с номерами строк
        code_lines_html = []
        for i, raw_line in enumerate((code or "").splitlines(), start=1):
            escaped = html.escape(raw_line)
            if raw_line.strip().startswith("*"):
                code_html = f'<span class="tok-comment">{escaped}</span>'
            elif ";" in escaped:
                parts = escaped.split(";", 1)
                code_html = f'{parts[0]}<span class="tok-comment">;{parts[1]}</span>'
            else:
                code_html = escaped
            code_lines_html.append(f'<tr><td class="num">{i}</td><td class="code">{code_html}</td></tr>')
        code_table_html = "".join(code_lines_html)

        # 1. Сводные показатели
        abs_c = parser.clocks.get("absolute", "Н/Д") if parser else "Н/Д"
        rel_c = parser.clocks.get("relative", abs_c) if parser else "Н/Д"
        total_blocks = parser.execution_stats.get("total_blocks", "Н/Д") if parser else "Н/Д"
        b_sec = parser.execution_stats.get("blocks_per_sec", "Н/Д") if parser else "Н/Д"
        gpss_ver = parser.header_info.get("version", "GPSS/H Release 3.70") if parser else "GPSS/H"

        # 2. Таблица приборов (Facilities)
        fac_rows_html = []
        bottlenecks = []
        if parser and parser.facilities:
            for f in parser.facilities:
                util = f.get("util", "0.0")
                try:
                    u_val = float(util)
                    if u_val >= 0.85:
                        bottlenecks.append(f"Высокая загрузка прибора <b>{html.escape(f['name'])}</b>: {u_val*100:.1f}%. Возможна нехватка пропускной способности.")
                except ValueError:
                    pass
                fac_rows_html.append(f"""
                    <tr>
                        <td><b>{html.escape(f['name'])}</b></td>
                        <td class="center">{f.get('util', '')}</td>
                        <td class="center">{f.get('entries', '')}</td>
                        <td class="center">{f.get('avg_time', '')}</td>
                        <td class="center">{html.escape(f.get('status', ''))}</td>
                    </tr>
                """)
        else:
            fac_rows_html.append('<tr><td colspan="5" class="empty">Нет активных приборов</td></tr>')

        # 3. Таблица очередей (Queues)
        q_rows_html = []
        if parser and parser.queues:
            for q in parser.queues:
                pct_z = q.get('pct_z') or q.get('pct_zero', '0.0')
                avg_t = q.get('avg_t') or q.get('avg_time', '0.000')
                q_rows_html.append(f"""
                    <tr>
                        <td><b>{html.escape(q['name'])}</b></td>
                        <td class="center">{q.get('max_c', '')}</td>
                        <td class="center">{q.get('avg_c', '')}</td>
                        <td class="center">{q.get('total_e', '')}</td>
                        <td class="center">{q.get('zero_e', '')}</td>
                        <td class="center">{pct_z}%</td>
                        <td class="center">{avg_t}</td>
                    </tr>
                """)
        else:
            q_rows_html.append('<tr><td colspan="7" class="empty">Нет очередей</td></tr>')

        # 4. Таблица накопителей (Storages)
        st_rows_html = []
        if parser and parser.storages:
            for s in parser.storages:
                st_rows_html.append(f"""
                    <tr>
                        <td><b>{html.escape(s['name'])}</b></td>
                        <td class="center">{s.get('capacity', '')}</td>
                        <td class="center">{s.get('avg_contents', '')}</td>
                        <td class="center">{s.get('util', '')}</td>
                        <td class="center">{s.get('max_contents', '')}</td>
                    </tr>
                """)
        else:
            st_rows_html.append('<tr><td colspan="5" class="empty">Нет многоканальных устройств (STORAGE)</td></tr>')

        # 5. Блоки (Block Counts)
        block_rows_html = []
        if parser and parser.blocks:
            for b in parser.blocks:
                block_rows_html.append(f"""
                    <tr>
                        <td class="center">Блок #{html.escape(b['block'])}</td>
                        <td class="center">{b.get('current', '0')}</td>
                        <td class="center">{b.get('total', '0')}</td>
                    </tr>
                """)
        else:
            block_rows_html.append('<tr><td colspan="3" class="empty">Данные о блоках отсутствуют</td></tr>')

        fac_table_body = "".join(fac_rows_html)
        q_table_body = "".join(q_rows_html)
        st_table_body = "".join(st_rows_html)
        block_table_body = "".join(block_rows_html)

        bottlenecks_html = ""
        if bottlenecks:
            items = "".join(f"<li>{b}</li>" for b in bottlenecks)
            bottlenecks_html = f"""
            <div class="warning-box">
                <h3>⚠️ Анализ узких мест системы (Bottlenecks)</h3>
                <ul>{items}</ul>
            </div>
            """

        html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчёт моделирования: {safe_model_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 30px;
            background-color: #f8fafc;
            color: #1e293b;
            line-height: 1.5;
        }}
        .container {{
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin-top: 0;
            color: #0f172a;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 12px;
            font-size: 26px;
        }}
        h2 {{
            color: #1e293b;
            margin-top: 28px;
            margin-bottom: 12px;
            font-size: 19px;
            border-bottom: 1px solid #edf2f7;
            padding-bottom: 6px;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .meta-card {{
            background: #f1f5f9;
            padding: 14px;
            border-radius: 6px;
            border-left: 4px solid #2563eb;
        }}
        .meta-label {{
            font-size: 12px;
            text-transform: uppercase;
            color: #64748b;
            font-weight: 600;
        }}
        .meta-val {{
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 4px;
        }}
        table.report-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
            margin-bottom: 24px;
            font-size: 14px;
            background: #ffffff;
        }}
        table.report-table th, table.report-table td {{
            padding: 10px 14px;
            border: 1px solid #e2e8f0;
            text-align: left;
        }}
        table.report-table th {{
            background-color: #f1f5f9;
            color: #334155;
            font-weight: 600;
            font-size: 13px;
        }}
        table.report-table tbody tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        table.report-table tbody tr:hover {{
            background-color: #f1f5f9;
        }}
        .center {{ text-align: center; }}
        .empty {{ text-align: center; color: #94a3b8; font-style: italic; }}
        
        .code-container {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            overflow-x: auto;
            margin: 16px 0 24px 0;
            font-family: Consolas, "Courier New", monospace;
            font-size: 13px;
        }}
        .code-table {{
            width: 100%;
            border: none;
            margin: 0;
            border-collapse: collapse;
        }}
        .code-table tr {{
            background: transparent !important;
        }}
        .code-table td {{
            border: none;
            padding: 2px 8px;
            color: #1e293b;
        }}
        .code-table td.num {{
            width: 45px;
            text-align: right;
            color: #94a3b8;
            user-select: none;
            background: #f1f5f9;
            border-right: 1px solid #e2e8f0;
            padding-right: 10px;
        }}
        .code-table td.code {{
            white-space: pre;
            padding-left: 12px;
        }}
        .tok-comment {{
            color: #64748b;
            font-style: italic;
        }}
        .warning-box {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-left: 5px solid #ef4444;
            padding: 14px 18px;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .warning-box h3 {{
            margin: 0 0 8px 0;
            color: #991b1b;
            font-size: 16px;
        }}
        .warning-box ul {{
            margin: 0;
            padding-left: 20px;
            color: #7f1d1d;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
            border-top: 1px solid #e2e8f0;
            padding-top: 14px;
        }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .container {{ box-shadow: none; padding: 0; }}
            .code-container {{ background: #f8fafc; color: #000; border: 1px solid #e2e8f0; }}
            .code-table td.num {{ background: #eee; color: #666; }}
            table, .meta-card, .warning-box {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Научно-технический отчёт по имитационному моделированию</h1>
        
        <div class="meta-grid">
            <div class="meta-card">
                <div class="meta-label">Файл модели</div>
                <div class="meta-val">{safe_model_name}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Модельное время (Clock)</div>
                <div class="meta-val">{abs_c} тактов</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Всего блоков выполнено</div>
                <div class="meta-val">{total_blocks}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Скорость симуляции</div>
                <div class="meta-val">{b_sec} бл/сек</div>
            </div>
        </div>

        {bottlenecks_html}

        <h2>1. Обслуживающие приборы (Facilities)</h2>
        <table class="report-table">
            <thead>
                <tr>
                    <th>Прибор</th>
                    <th class="center">Загрузка (Avg-Util)</th>
                    <th class="center">Заявок (Entries)</th>
                    <th class="center">Ср. время обслуживания</th>
                    <th class="center">Итоговый статус</th>
                </tr>
            </thead>
            <tbody>
                {fac_table_body}
            </tbody>
        </table>

        <h2>2. Очереди ожидания (Queues)</h2>
        <table class="report-table">
            <thead>
                <tr>
                    <th>Очередь</th>
                    <th class="center">Макс. длина</th>
                    <th class="center">Ср. длина</th>
                    <th class="center">Всего входов</th>
                    <th class="center">Без ожидания</th>
                    <th class="center">% без ожидания</th>
                    <th class="center">Ср. время ожидания</th>
                </tr>
            </thead>
            <tbody>
                {q_table_body}
            </tbody>
        </table>

        <h2>3. Многоканальные накопители (Storages)</h2>
        <table class="report-table">
            <thead>
                <tr>
                    <th>Накопитель</th>
                    <th class="center">Ёмкость (Каналов)</th>
                    <th class="center">Ср. занятость</th>
                    <th class="center">Загрузка (Avg-Util)</th>
                    <th class="center">Макс. занятость</th>
                </tr>
            </thead>
            <tbody>
                {st_table_body}
            </tbody>
        </table>

        <h2>4. Счётчики блоков модели (Block Executions)</h2>
        <table class="report-table">
            <thead>
                <tr>
                    <th class="center">Номер блока</th>
                    <th class="center">Текущее число транзактов</th>
                    <th class="center">Всего транзактов прошло</th>
                </tr>
            </thead>
            <tbody>
                {block_table_body}
            </tbody>
        </table>

        <h2>5. Исходный код модели GPSS</h2>
        <div class="code-container">
            <table class="code-table">
                {code_table_html}
            </table>
        </div>

        <div class="footer">
            Сформировано в GPSS/H Studio • {now_str} • {gpss_ver}
        </div>
    </div>
</body>
</html>
        """
        return html_template

    @classmethod
    def export_report_dialog(cls, parent, model_name, code, parser):
        if not parser:
            QMessageBox.warning(parent, "Экспорт отчёта", "Сначала запустите симуляцию (F5), чтобы получить данные для отчёта.")
            return

        default_name = (os.path.splitext(model_name)[0] if model_name else "gpss_report") + ".html"
        save_path, _ = QFileDialog.getSaveFileName(
            parent, "Экспорт отчёта о моделировании", default_name, "HTML Отчёт (*.html);;Все файлы (*.*)"
        )
        if not save_path:
            return

        try:
            html_content = cls.generate_html(model_name, code, parser)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            reply = QMessageBox.question(
                parent, "Экспорт отчёта",
                f"Отчёт успешно сохранён:\n{save_path}\n\nОткрыть его в браузере для просмотра и печати в PDF?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(save_path))

        except Exception as e:
            QMessageBox.critical(parent, "Ошибка экспорта", f"Не удалось сформировать отчёт:\n{e}")

