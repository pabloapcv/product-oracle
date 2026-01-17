"""
Winner Engine Web Interface
Simple Flask app for viewing reports and managing the system.
"""
from flask import Flask, render_template, jsonify, request
from datetime import date, timedelta
from pathlib import Path
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'winner-engine-secret-key'

# Set SQLite mode
os.environ["USE_SQLITE"] = "true"


@app.route('/')
def index():
    """Main dashboard."""
    return render_template('index.html')


@app.route('/api/reports')
def list_reports():
    """List all available reports."""
    reports_dir = Path('reports')
    reports = []
    
    if reports_dir.exists():
        for report_file in sorted(reports_dir.glob('*.json'), reverse=True):
            week_start = report_file.stem
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                    reports.append({
                        'week_start': week_start,
                        'generated_at': data.get('generated_at'),
                        'opportunity_count': len(data.get('opportunities', []))
                    })
            except:
                pass
    
    return jsonify(reports)


@app.route('/api/report/<week_start>')
def get_report(week_start):
    """Get report for a specific week."""
    report_path = Path('reports') / f'{week_start}.json'
    
    if not report_path.exists():
        return jsonify({'error': 'Report not found'}), 404
    
    with open(report_path, 'r') as f:
        return jsonify(json.load(f))


@app.route('/api/opportunities/<week_start>')
def get_opportunities(week_start):
    """Get top opportunities for a week."""
    report_path = Path('reports') / f'{week_start}.json'
    
    if not report_path.exists():
        return jsonify({'error': 'Report not found'}), 404
    
    with open(report_path, 'r') as f:
        data = json.load(f)
        top_n = request.args.get('top_n', 50, type=int)
        opportunities = data.get('opportunities', [])[:top_n]
        
        return jsonify({
            'week_start': week_start,
            'opportunities': opportunities,
            'total': len(data.get('opportunities', []))
        })


@app.route('/api/stats')
def get_stats():
    """Get system statistics."""
    from src.utils.db import execute_query
    
    try:
        entity_count = execute_query('SELECT COUNT(*) as c FROM entities')[0]['c']
        amazon_count = execute_query('SELECT COUNT(*) as c FROM amazon_listings_daily')[0]['c']
        tiktok_count = execute_query('SELECT COUNT(*) as c FROM tiktok_metrics_daily')[0]['c']
        
        # Get latest report
        reports_dir = Path('reports')
        latest_report = None
        if reports_dir.exists():
            report_files = sorted(reports_dir.glob('*.json'), reverse=True)
            if report_files:
                latest_report = report_files[0].stem
        
        return jsonify({
            'entities': entity_count,
            'amazon_listings': amazon_count,
            'tiktok_metrics': tiktok_count,
            'latest_report': latest_report
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/entities')
def get_entities():
    """Get list of entities."""
    from src.utils.db import execute_query
    
    try:
        limit = request.args.get('limit', 50, type=int)
        entities = execute_query(
            'SELECT entity_id, canonical_name, category_primary FROM entities LIMIT ?',
            (limit,)
        )
        return jsonify(entities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/entity/<entity_id>')
def get_entity_details(entity_id):
    """Get details for a specific entity."""
    from src.utils.db import execute_query
    
    try:
        entity = execute_query(
            'SELECT * FROM entities WHERE entity_id = ?',
            (entity_id,)
        )
        
        if not entity:
            return jsonify({'error': 'Entity not found'}), 404
        
        # Get aliases
        aliases = execute_query(
            'SELECT * FROM entity_aliases WHERE entity_id = ?',
            (entity_id,)
        )
        
        entity[0]['aliases'] = aliases
        
        return jsonify(entity[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

