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


@app.route('/api/entity/<entity_id>/stats')
def get_entity_stats(entity_id):
    """Get aggregated statistics for an entity."""
    from src.utils.db import execute_query
    
    try:
        # Verify entity exists (but don't fail if it doesn't - return empty data)
        entity_check = execute_query(
            'SELECT entity_id FROM entities WHERE entity_id = ?',
            (entity_id,)
        )
        
        if not entity_check:
            # Return 200 with empty data instead of 404, so frontend can handle gracefully
            return jsonify({
                'latest_score': None,
                'amazon': {},
                'tiktok': {},
                'note': 'Entity not found'
            }), 200
        
        # Get latest week's score
        latest_score = execute_query("""
            SELECT score_winner_prob, score_demand, score_competition, 
                   score_margin, score_risk, week_start
            FROM entity_weekly_scores
            WHERE entity_id = ?
            ORDER BY week_start DESC
            LIMIT 1
        """, (entity_id,))
        
        # Initialize default data structures
        amazon_data = {}
        tiktok_data = {}
        
        # Get Amazon aliases
        try:
            amazon_aliases = execute_query("""
                SELECT alias_text FROM entity_aliases 
                WHERE entity_id = ? AND source = 'amazon'
            """, (entity_id,))
            
            if amazon_aliases and len(amazon_aliases) > 0:
                alias_list = [a['alias_text'] for a in amazon_aliases]
                placeholders = ','.join(['?' for _ in alias_list])
                
                # Count Amazon listings
                amazon_count = execute_query(f"""
                    SELECT COUNT(DISTINCT asin) as count,
                           AVG(price_usd) as avg_price,
                           MIN(bsr) as best_bsr,
                           AVG(rating) as avg_rating,
                           SUM(review_count) as total_reviews
                    FROM amazon_listings_daily
                    WHERE asin IN ({placeholders})
                """, tuple(alias_list))
                
                if amazon_count and len(amazon_count) > 0 and amazon_count[0].get('count', 0):
                    row = amazon_count[0]
                    amazon_data = {
                        'count': int(row.get('count', 0) or 0),
                        'avg_price': float(row.get('avg_price', 0) or 0),
                        'best_bsr': row.get('best_bsr'),
                        'avg_rating': float(row.get('avg_rating', 0) or 0),
                        'total_reviews': int(row.get('total_reviews', 0) or 0)
                    }
        except Exception as e:
            # Log but don't fail - just return empty amazon_data
            import logging
            logging.warning(f"Error fetching Amazon stats for {entity_id}: {e}")
        
        # Get TikTok aliases
        try:
            tiktok_aliases = execute_query("""
                SELECT alias_text FROM entity_aliases 
                WHERE entity_id = ? AND source = 'tiktok'
            """, (entity_id,))
            
            if tiktok_aliases and len(tiktok_aliases) > 0:
                alias_list = [a['alias_text'] for a in tiktok_aliases]
                placeholders = ','.join(['?' for _ in alias_list])
                
                # Count TikTok metrics
                tiktok_count = execute_query(f"""
                    SELECT COUNT(DISTINCT query) as count,
                           MAX(views) as max_views,
                           MAX(videos) as max_videos,
                           MAX(creator_count) as max_creators
                    FROM tiktok_metrics_daily
                    WHERE query IN ({placeholders})
                """, tuple(alias_list))
                
                if tiktok_count and len(tiktok_count) > 0 and tiktok_count[0].get('count', 0):
                    row = tiktok_count[0]
                    tiktok_data = {
                        'count': int(row.get('count', 0) or 0),
                        'max_views': int(row.get('max_views', 0) or 0),
                        'max_videos': int(row.get('max_videos', 0) or 0),
                        'max_creators': int(row.get('max_creators', 0) or 0)
                    }
        except Exception as e:
            # Log but don't fail - just return empty tiktok_data
            import logging
            logging.warning(f"Error fetching TikTok stats for {entity_id}: {e}")
        
        # Always return 200 with data structures, even if empty
        return jsonify({
            'latest_score': latest_score[0] if latest_score and len(latest_score) > 0 else None,
            'amazon': amazon_data,
            'tiktok': tiktok_data
        })
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Error in get_entity_stats for {entity_id}: {e}")
        logging.error(traceback.format_exc())
        # Return 200 with error info instead of 500, so frontend can handle gracefully
        return jsonify({
            'error': str(e),
            'latest_score': None,
            'amazon': {},
            'tiktok': {}
        }), 200  # Changed to 200 so frontend doesn't treat as failure


if __name__ == '__main__':
    import sys
    
    # Use port 5001 to avoid macOS AirPlay conflict on port 5000
    port = 5001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    print("=" * 60)
    print("Winner Engine Web Interface")
    print("=" * 60)
    print()
    print("🌐 Server starting...")
    print(f"   URL: http://localhost:{port}")
    print("   Press Ctrl+C to stop")
    print()
    try:
        app.run(debug=True, host='127.0.0.1', port=port, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()

