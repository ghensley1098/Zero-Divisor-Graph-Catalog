# server_app.py
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from database import ZeroDivisorDatabase
import json
import csv
import io
from threading import Lock

app = Flask(__name__)
CORS(app)

db = ZeroDivisorDatabase()
db_lock = Lock()

def parse_component_filter(component_filter):
    """Parse component filter with wildcard support"""
    components = []
    if not component_filter or not component_filter.strip():
        return components

    parts = []
    current_part = ""
    paren_depth = 0
    for char in component_filter:
        if char == '(':
            paren_depth += 1
            current_part += char
        elif char == ')':
            paren_depth -= 1
            current_part += char
        elif char == ',' and paren_depth == 0:
            parts.append(current_part.strip())
            current_part = ""
        else:
            current_part += char
    if current_part.strip():
        parts.append(current_part.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith('(') and part.endswith(')'):
            try:
                inner = part[1:-1]
                a_str, b_str = [x.strip() for x in inner.split(',')]
                p1 = None if a_str == '' else int(a_str) if a_str else None
                p2 = None if b_str == '' else int(b_str) if b_str else None
                components.append({'type': 'bipartite', 'p1': p1, 'p2': p2})
            except:
                raise ValueError(f"Invalid bipartite: {part}")
        else:
            try:
                if part == '':
                    components.append({'type': 'complete_wildcard', 'p1': None})
                else:
                    components.append({'type': 'complete', 'p1': int(part)})
            except:
                raise ValueError(f"Invalid complete: {part}")
    return components

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Server running'})

@app.route('/api/entries')
def get_entries():
    try:
        start_n = request.args.get('start_n', 1, type=int)
        end_n = request.args.get('end_n', 100, type=int)
        component_filter = request.args.get('components', '')
        exact_match = request.args.get('exact_match', 'false') == 'true'
        component_type = request.args.get('component_type', '')

        query = '''
            SELECT mn.nvalue, mn.exact_components_desc, mn.partition_count,
                   mn.zvertices_count, mn.zedges_count, mn.ezvertices_count, mn.ezedges_count,
                   mn.complete, mn.complete_bipartite
            FROM MyNumber mn
            WHERE mn.nvalue BETWEEN ? AND ?
        '''
        params = [start_n, end_n]

        if component_filter:
            components = parse_component_filter(component_filter)
            conditions = []
            cparams = []
            for comp in components:
                if comp['type'] == 'bipartite':
                    if comp['p1'] is None and comp['p2'] is None:
                        conditions.append("EXISTS (SELECT 1 FROM ExactConnection ec WHERE ec.entry_id = mn.entry_id AND ec.component_type = 'bipartite')")
                    elif comp['p1'] is None:
                        conditions.append("EXISTS (SELECT 1 FROM ExactConnection ec WHERE ec.entry_id = mn.entry_id AND ec.component_type = 'bipartite' AND ec.p2 = ?)")
                        cparams.append(comp['p2'])
                    elif comp['p2'] is None:
                        conditions.append("EXISTS (SELECT 1 FROM ExactConnection ec WHERE ec.entry_id = mn.entry_id AND ec.component_type = 'bipartite' AND ec.p1 = ?)")
                        cparams.append(comp['p1'])
                    else:
                        conditions.append("EXISTS (SELECT 1 FROM ExactConnection ec WHERE ec.entry_id = mn.entry_id AND ec.component_type = 'bipartite' AND ec.p1 = ? AND ec.p2 = ?)")
                        cparams.extend([comp['p1'], comp['p2']])
                elif comp['type'] == 'complete':
                    conditions.append("EXISTS (SELECT 1 FROM ExactConnection ec WHERE ec.entry_id = mn.entry_id AND ec.component_type = 'complete' AND ec.p1 = ? AND ec.p2 IS NULL)")
                    cparams.append(comp['p1'])
            if conditions:
                query += ' AND ' + ' AND '.join(conditions)
                params.extend(cparams)
                if exact_match:
                    query += f' AND mn.partition_count = {len(components)}'

        if component_type == 'complete':
            query += ' AND mn.complete > 0'
        elif component_type == 'bipartite':
            query += ' AND mn.complete_bipartite > 0'

        query += ' ORDER BY mn.nvalue'

        with db_lock:
            conn = db._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

        entries = []
        for row in results:
            entry = {
                'n': row[0],
                'exact_components': row[1] if row[1] else 'None',
                'partition_count': row[2],
                'zvertices_count': row[3],
                'zedges_count': row[4],
                'ezvertices_count': row[5],
                'ezedges_count': row[6],
                'has_complete': row[7] > 0,
                'has_bipartite': row[8] > 0,
                'can_generate_graph': row[0] <= 5500
            }
            entries.append(entry)

        return jsonify({'success': True, 'entries': entries, 'total': len(entries)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/csv')
def export_csv():
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'n', 'exact_components', 'partition_count',
            'zvertices_count', 'zedges_count',
            'ezvertices_count', 'ezedges_count',
            'complete_components', 'bipartite_components'
        ])

        with db_lock:
            conn = db._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT nvalue, exact_components_desc, partition_count,
                       zvertices_count, zedges_count, ezvertices_count, ezedges_count,
                       complete, complete_bipartite
                FROM MyNumber ORDER BY nvalue
            ''')
            results = cursor.fetchall()
            conn.close()

        for row in results:
            writer.writerow([row[0], row[1] or '', row[2], row[3], row[4], row[5], row[6], row[7], row[8]])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='zero_divisor_catalog.csv'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/graph/<int:n>')
def get_graph(n):
    try:
        if n > 5500:
            return jsonify({'success': False, 'error': f'Graph generation not available for n > 5500'}), 400

        data = db.get_by_n(n)
        if not data:
            return jsonify({'success': False, 'error': f'No data found for Z_{n}'}), 404

        if data.get('z_structure') in ('0', None) or data.get('ez_structure') in ('0', None):
            return jsonify({'success': False, 'error': 'Structure data not available'}), 404

        return jsonify({
            'success': True,
            'data': {
                'n': n,
                'zero_divisor_graph': data['z_structure'],
                'exact_zero_divisor_graph': data['ez_structure'],
                'components': data['exact_components_desc']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)