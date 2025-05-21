from flask import Flask, render_template, request, jsonify
from src.main import run_hedge_fund
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# List of available analysts
ANALYSTS = [
    {"id": "warren_buffett", "name": "Warren Buffett", "description": "Value investing with emphasis on quality and safety"},
    {"id": "cathie_wood", "name": "Cathie Wood", "description": "Disruptive technology and innovation"},
    {"id": "michael_burry", "name": "Michael Burry", "description": "Deep value and contrarian investing"},
    {"id": "peter_lynch", "name": "Peter Lynch", "description": "Growth at a reasonable price (GARP)"},
    {"id": "technical", "name": "Technical Analysis", "description": "Price action and technical indicators"},
    {"id": "fundamental", "name": "Fundamental Analysis", "description": "Traditional financial metrics"},
    {"id": "sentiment", "name": "Sentiment Analysis", "description": "Market sentiment and news"},
    {"id": "valuation", "name": "Valuation", "description": "Intrinsic value calculation"}
]

@app.route('/')
def index():
    return render_template('index.html', analysts=ANALYSTS)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    tickers = [ticker.strip() for ticker in data['tickers'].split(',')]
    selected_analysts = data['analysts']
    
    # Set default dates if not provided
    end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    start_date = data.get('start_date', (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'))
    
    # Initial portfolio setup
    portfolio = {
        "positions": {},
        "total_cash": float(data.get('initial_cash', 100000.0))
    }
    
    try:
        result = run_hedge_fund(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            portfolio=portfolio,
            show_reasoning=True,
            selected_analysts=selected_analysts,
            model_name=data.get('model_name', 'gpt-4'),
            model_provider=data.get('model_provider', 'OpenAI')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 