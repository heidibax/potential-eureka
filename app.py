from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from user import User, Portfolio
import uuid
from datetime import datetime
import json

# Import game logic from main.py
from main import (
    COMPANIES, POINTS, premium_picks, mid_tier, wildcards, risky_plays,
    eps_outcome, score_company_game, stock_market_reaction, price_change_1month,
    earnings_rows, game_score
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage (replace with database in production)
users = {}
user_counter = 0

# Stock pricing (simplified - in production, fetch real-time prices)
STOCK_PRICES = {
    "premium": 15,
    "mid_tier": 10,
    "wildcard": 5,
    "risky": 3
}

def get_stock_price(ticker):
    """Get the price category for a stock"""
    if ticker in premium_picks:
        return STOCK_PRICES["premium"]
    elif ticker in mid_tier:
        return STOCK_PRICES["mid_tier"]
    elif ticker in wildcards:
        return STOCK_PRICES["wildcard"]
    elif ticker in risky_plays:
        return STOCK_PRICES["risky"]
    return 0

#  USER ENDPOINTS 

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    global user_counter
    data = request.json
    
    user_id = str(uuid.uuid4())
    username = data.get('username')
    email = data.get('email', '')
    initial_balance = data.get('initial_balance', 100.0)
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    user = User(user_id, username, email, initial_balance)
    users[user_id] = user
    
    user_data = user.get_user()
    # Convert datetime to string for JSON serialization
    if 'created_at' in user_data and isinstance(user_data['created_at'], datetime):
        user_data['created_at'] = user_data['created_at'].isoformat()
    
    return jsonify(user_data), 201

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = users[user_id].get_user()
    # Convert datetime to string for JSON serialization
    if 'created_at' in user_data and isinstance(user_data['created_at'], datetime):
        user_data['created_at'] = user_data['created_at'].isoformat()
    # Convert datetime objects in inbox
    if 'inbox' in user_data:
        for msg in user_data['inbox']:
            if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
                msg['timestamp'] = msg['timestamp'].isoformat()
    
    return jsonify(user_data)

@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users"""
    users_list = []
    for user in users.values():
        user_data = user.get_user()
        # Convert datetime to string for JSON serialization
        if 'created_at' in user_data and isinstance(user_data['created_at'], datetime):
            user_data['created_at'] = user_data['created_at'].isoformat()
        # Convert datetime objects in inbox
        if 'inbox' in user_data:
            for msg in user_data['inbox']:
                if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
                    msg['timestamp'] = msg['timestamp'].isoformat()
        users_list.append(user_data)
    return jsonify(users_list)

#  PORTFOLIO ENDPOINTS 

@app.route('/api/users/<user_id>/portfolio', methods=['GET'])
def get_portfolio(user_id):
    """Get user's portfolio"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[user_id]
    portfolio_data = {
        'holdings': user.portfolio.holdings,
        'balance': user.balance,
        'total_value': user.balance  # Simplified - add stock value calculation
    }
    
    return jsonify(portfolio_data)

@app.route('/api/users/<user_id>/portfolio/buy', methods=['POST'])
def buy_stock(user_id):
    """Buy stocks for user's portfolio"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    ticker = data.get('ticker', '').upper()
    shares = int(data.get('shares', 1))
    
    if ticker not in COMPANIES:
        return jsonify({'error': f'Stock {ticker} not available'}), 400
    
    user = users[user_id]
    price_per_share = get_stock_price(ticker)
    total_cost = price_per_share * shares
    
    if not user.can_afford(price_per_share, shares):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    user.portfolio.add_stock(ticker, shares)
    user.update_balance(-total_cost)
    
    return jsonify({
        'message': f'Bought {shares} shares of {ticker}',
        'balance': user.balance,
        'portfolio': user.portfolio.holdings
    })

@app.route('/api/users/<user_id>/portfolio/sell', methods=['POST'])
def sell_stock(user_id):
    """Sell stocks from user's portfolio"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    ticker = data.get('ticker', '').upper()
    shares = int(data.get('shares', 1))
    
    user = users[user_id]
    
    try:
        user.portfolio.remove_stock(ticker, shares)
        price_per_share = get_stock_price(ticker)
        total_revenue = price_per_share * shares
        user.update_balance(total_revenue)
        
        return jsonify({
            'message': f'Sold {shares} shares of {ticker}',
            'balance': user.balance,
            'portfolio': user.portfolio.holdings
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

#  STOCK/COMPANY ENDPOINTS 

@app.route('/api/stocks', methods=['GET'])
def get_available_stocks():
    """Get list of all available stocks with their prices"""
    stocks = []
    for ticker in COMPANIES:
        price = get_stock_price(ticker)
        category = "premium" if ticker in premium_picks else \
                   "mid_tier" if ticker in mid_tier else \
                   "wildcard" if ticker in wildcards else "risky"
        stocks.append({
            'ticker': ticker,
            'price': price,
            'category': category
        })
    
    return jsonify(stocks)

@app.route('/api/stocks/<ticker>/earnings', methods=['GET'])
def get_stock_earnings(ticker):
    """Get earnings data for a specific stock"""
    ticker = ticker.upper()
    if ticker not in COMPANIES:
        return jsonify({'error': 'Stock not found'}), 404
    
    try:
        earnings_data = earnings_rows(ticker)
        if earnings_data:
            return jsonify(earnings_data)
        else:
            return jsonify({'error': 'No earnings data available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#  GAME SCORING ENDPOINTS 

@app.route('/api/game/scores', methods=['GET'])
def get_game_scores():
    """Get game scores for all companies"""
    try:
        scores = game_score
        return jsonify(scores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/score', methods=['GET'])
def get_user_score(user_id):
    """Calculate and return user's total game score based on their portfolio"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[user_id]
    portfolio = user.portfolio.holdings
    
    try:
        all_scores = game_score
        total_score = 0
        portfolio_scores = []
        
        for ticker, shares in portfolio.items():
            # Find score for this ticker
            ticker_score = next((s for s in all_scores if s['ticker'] == ticker), None)
            if ticker_score:
                score_value = ticker_score['game_score'] * shares  # Multiply by shares owned
                total_score += score_value
                portfolio_scores.append({
                    'ticker': ticker,
                    'shares': shares,
                    'score_per_share': ticker_score['game_score'],
                    'total_score': score_value,
                    'breakdown': ticker_score.get('breakdown', {})
                })
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'total_score': total_score,
            'portfolio_scores': portfolio_scores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#  SOCIAL ENDPOINTS 

@app.route('/api/users/<user_id>/follow/<target_user_id>', methods=['POST'])
def follow_user(user_id, target_user_id):
    """Follow another user"""
    if user_id not in users or target_user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    users[user_id].follow(users[target_user_id])
    return jsonify({'message': 'User followed successfully'})

@app.route('/api/users/<user_id>/unfollow/<target_user_id>', methods=['POST'])
def unfollow_user(user_id, target_user_id):
    """Unfollow another user"""
    if user_id not in users or target_user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    users[user_id].unfollow(users[target_user_id])
    return jsonify({'message': 'User unfollowed successfully'})

@app.route('/api/users/<user_id>/messages', methods=['GET'])
def get_messages(user_id):
    """Get user's inbox messages"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    messages = users[user_id].receive_messages()
    # Convert datetime objects to strings
    for msg in messages:
        if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
            msg['timestamp'] = msg['timestamp'].isoformat()
    
    return jsonify(messages)

@app.route('/api/users/<user_id>/messages', methods=['POST'])
def send_message(user_id):
    """Send a message to another user"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    recipient_id = data.get('recipient_id')
    message = data.get('message')
    
    if not recipient_id or recipient_id not in users:
        return jsonify({'error': 'Recipient not found'}), 404
    
    users[user_id].send_message(users[recipient_id], message)
    return jsonify({'message': 'Message sent successfully'})

#  HEALTH CHECK 

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

#  ROOT ROUTES 

@app.route('/', methods=['GET'])
def index():
    """Serve the main website"""
    try:
        return send_from_directory('fantasy-earnings', 'index.html')
    except:
        return jsonify({
            'error': 'index.html not found',
            'message': 'Make sure fantasy-earnings/index.html exists'
        }), 404

@app.route('/example', methods=['GET'])
def serve_example():
    """Serve the example frontend HTML file"""
    try:
        return send_from_directory('.', 'example_frontend.html')
    except:
        return jsonify({
            'error': 'Example file not found',
            'instructions': 'Open example_frontend.html directly in your browser (file://) or place it in a static folder'
        }), 404

# FRONTEND API ENDPOINTS

@app.route('/companies', methods=['GET'])
def get_companies():
    """Get all companies with their data"""
    companies = []
    try:
        # Get company tier for pricing
        def get_tier(ticker):
            if ticker in premium_picks:
                return 'premium', 15
            elif ticker in mid_tier:
                return 'mid_tier', 10
            elif ticker in wildcards:
                return 'wildcard', 5
            else:
                return 'risky', 3
        
        # Build company list from earnings_rows data
        company_idx = 1
        for ticker, data in earnings_rows.items():
            tier, price = get_tier(ticker)
            
            company = {
                'id': company_idx,
                'name': data.get('stock name', ticker),
                'ticker': ticker,
                'tier': tier,
                'price': price,
                'earnings_date': data.get('earnings_date', 'N/A'),
                'img': f'img/{ticker.lower()}.png',
                'score': game_score.get(ticker, 0),
                'industry': 'Technology',  # You can enhance this later
                'breakdown': {
                    'eps_estimate': round(float(data.get('eps_estimate', 0)), 2),
                    'eps_actual': round(float(data.get('eps_actual', 0)), 2),
                    'eps_result': data.get('eps_result', 'N/A'),
                    'surprise_pct': round(float(data.get('surprise_pct', 0)), 2) if data.get('surprise_pct') else 0,
                    'bonus_flags': data.get('bonus_flags', []),
                    'daily_pct_change': data.get('daily_pct_change', 'N/A'),
                    'monthly_price_change': data.get('monthly_price_change', 'N/A'),
                    'tags': ', '.join(data.get('bonus_flags', []))
                }
            }
            companies.append(company)
            company_idx += 1
    except Exception as e:
        print(f"Error in get_companies: {e}")
        return jsonify({'error': str(e), 'earnings_rows_count': len(earnings_rows)}), 500
    
    return jsonify(companies)

@app.route('/companies/<company_id>', methods=['GET'])
def get_company(company_id):
    """Get a single company by ID"""
    try:
        companies_list = list(earnings_rows.items())
        idx = int(company_id) - 1
        if idx < 0 or idx >= len(companies_list):
            return jsonify({'error': 'Company not found'}), 404
        
        ticker, data = companies_list[idx]
        
        # Get company tier for pricing
        def get_tier(ticker):
            if ticker in premium_picks:
                return 'premium', 15
            elif ticker in mid_tier:
                return 'mid_tier', 10
            elif ticker in wildcards:
                return 'wildcard', 5
            else:
                return 'risky', 3
        
        tier, price = get_tier(ticker)
        
        company = {
            'id': idx + 1,
            'name': data.get('stock name', ticker),
            'ticker': ticker,
            'tier': tier,
            'price': price,
            'earnings_date': data.get('earnings_date', 'N/A'),
            'img': f'img/{ticker.lower()}.png',
            'score': game_score.get(ticker, 0),
            'industry': 'Technology',
            'breakdown': {
                'eps_estimate': round(float(data.get('eps_estimate', 0)), 2),
                'eps_actual': round(float(data.get('eps_actual', 0)), 2),
                'eps_result': data.get('eps_result', 'N/A'),
                'surprise_pct': round(float(data.get('surprise_pct', 0)), 2) if data.get('surprise_pct') else 0,
                'bonus_flags': data.get('bonus_flags', []),
                'daily_pct_change': data.get('daily_pct_change', 'N/A'),
                'monthly_price_change': data.get('monthly_price_change', 'N/A'),
                'tags': ', '.join(data.get('bonus_flags', []))
            }
        }
        return jsonify(company)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the leaderboard with all players and scores"""
    try:
        leaderboard = []
        for user_id, user in users.items():
            user_data = user.get_user()
            leaderboard.append({
                'player_id': user_id,
                'player_name': user_data.get('username', 'Unknown'),
                'score': user_data.get('balance', 0)
            })
        # Sort by score descending
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DRAFT/PORTFOLIO ENDPOINTS

@app.route('/api/draft', methods=['GET'])
def get_draft():
    """Get the current user's draft (portfolio)"""
    try:
        # For now, we'll use a simple session or user ID
        # In production, you'd track which user is making the request
        user_id = request.args.get('user_id')
        if not user_id or user_id not in users:
            return jsonify({'error': 'User not found'}), 404
        
        user = users[user_id]
        user_data = user.get_user()
        portfolio = user_data.get('portfolio', {})
        
        # Format portfolio for frontend
        draft = []
        for ticker, shares in portfolio.items():
            if ticker in earnings_rows:
                data = earnings_rows[ticker]
                draft.append({
                    'id': list(earnings_rows.keys()).index(ticker) + 1,
                    'ticker': ticker,
                    'name': data.get('stock name', ticker),
                    'shares': shares,
                    'price': get_stock_price(ticker),
                    'total_cost': shares * get_stock_price(ticker)
                })
        
        return jsonify(draft)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/draft', methods=['POST'])
def add_to_draft():
    """Add a company to the current user's draft"""
    try:
        data = request.json
        user_id = data.get('user_id')
        company_id = data.get('id')
        shares = data.get('shares', 1)
        
        if not user_id or user_id not in users:
            return jsonify({'error': 'User not found'}), 404
        
        # Get the ticker from company_id
        companies_list = list(earnings_rows.items())
        if company_id < 1 or company_id > len(companies_list):
            return jsonify({'error': 'Company not found'}), 404
        
        ticker, _ = companies_list[company_id - 1]
        
        user = users[user_id]
        price_per_share = get_stock_price(ticker)
        total_cost = price_per_share * shares
        
        # Check if user can afford
        if total_cost > user.balance:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # Add to portfolio
        user.portfolio.add_stock(ticker, shares)
        user.update_balance(-total_cost)
        
        return jsonify({
            'success': True,
            'message': f'Added {shares} share(s) of {ticker}',
            'remaining_balance': user.balance
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/draft/<company_id>', methods=['DELETE'])
def remove_from_draft(company_id):
    """Remove a company from the current user's draft"""
    try:
        user_id = request.args.get('user_id')
        shares = request.args.get('shares', 1, type=int)
        
        if not user_id or user_id not in users:
            return jsonify({'error': 'User not found'}), 404
        
        # Get the ticker from company_id
        companies_list = list(earnings_rows.items())
        if int(company_id) < 1 or int(company_id) > len(companies_list):
            return jsonify({'error': 'Company not found'}), 404
        
        ticker, _ = companies_list[int(company_id) - 1]
        
        user = users[user_id]
        price_per_share = get_stock_price(ticker)
        refund = price_per_share * shares
        
        # Remove from portfolio
        user.portfolio.remove_stock(ticker, shares)
        user.update_balance(refund)
        
        return jsonify({
            'success': True,
            'message': f'Removed {shares} share(s) of {ticker}',
            'refund': refund,
            'remaining_balance': user.balance
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/draft/simulate', methods=['POST'])
def simulate_earnings():
    """Simulate earnings and calculate scores for draft"""
    try:
        user_id = request.json.get('user_id')
        
        if not user_id or user_id not in users:
            return jsonify({'error': 'User not found'}), 404
        
        user = users[user_id]
        user_data = user.get_user()
        portfolio = user_data.get('portfolio', {})
        
        # Calculate total score
        total_score = 0
        results = []
        
        for ticker, shares in portfolio.items():
            if ticker in game_score:
                score_per_share = game_score[ticker]
                total_shares_score = score_per_share * shares
                total_score += total_shares_score
                
                results.append({
                    'ticker': ticker,
                    'shares': shares,
                    'score_per_share': score_per_share,
                    'total_score': total_shares_score
                })
        
        return jsonify({
            'user_id': user_id,
            'total_score': total_score,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from root directory"""
    return send_from_directory('.', filename)

@app.route('/style.css')
def serve_style():
    """Serve CSS from fantasy-earnings folder"""
    return send_from_directory('fantasy-earnings', 'style.css')

@app.route('/<path:filename>')
def serve_files(filename):
    """Serve files from fantasy-earnings folder (CSS, JS, images, etc)"""
    try:
        return send_from_directory('fantasy-earnings', filename)
    except:
        try:
            return send_from_directory('.', filename)
        except:
            return jsonify({'error': f'File {filename} not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
