from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Game state storage (in-memory for simplicity)
game_state = {
    'current_question': None,
    'question_enabled': False,
    'question_locked': False,
    'teams': {},  # team_number: {'name': str, 'score': int, 'answers': {question_id: answer}}
    'correct_answer': None
}

# Load questions from JSON file
def load_questions():
    questions_file = os.path.join(os.path.dirname(__file__), 'questions.json')
    with open(questions_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_questions(data):
    """Save questions to JSON file"""
    questions_file = os.path.join(os.path.dirname(__file__), 'questions.json')
    with open(questions_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

questions_data = load_questions()

@app.route('/')
def index():
    """Team selection page"""
    return render_template('index.html')

@app.route('/team/<int:team_number>')
def team_view(team_number):
    """Team game view"""
    if team_number < 1 or team_number > app.config['MAX_TEAMS']:
        return "Invalid team number", 400
    
    # Initialize team if not exists
    if team_number not in game_state['teams']:
        game_state['teams'][team_number] = {
            'name': f'Team {team_number}',
            'score': 0,
            'answers': {}
        }
    
    return render_template('team.html', team_number=team_number)

@app.route(f"/{Config.ADMIN_URL}")
def admin_view():
    """Admin control panel"""
    return render_template('admin.html', questions=questions_data['questions'])

# API Endpoints
@app.route('/api/game-state')
def get_game_state():
    """Get current game state for teams"""
    return jsonify({
        'current_question': game_state['current_question'],
        'question_enabled': game_state['question_enabled'],
        'question_locked': game_state['question_locked'],
        'question_data': questions_data['questions'][game_state['current_question']] if game_state['current_question'] is not None else None,
        'show_correct': game_state['question_locked'],
        'correct_answer': game_state['correct_answer'] if game_state['question_locked'] else None
    })

@app.route('/api/admin/game-state')
def get_admin_game_state():
    """Get full game state for admin"""
    return jsonify({
        'current_question': game_state['current_question'],
        'question_enabled': game_state['question_enabled'],
        'question_locked': game_state['question_locked'],
        'teams': game_state['teams'],
        'correct_answer': game_state['correct_answer']
    })

@app.route('/api/admin/enable-question', methods=['POST'])
def enable_question():
    """Enable a specific question"""
    data = request.json
    question_index = data.get('question_index')
    
    if question_index is None or question_index >= len(questions_data['questions']):
        return jsonify({'error': 'Invalid question index'}), 400
    
    game_state['current_question'] = question_index
    game_state['question_enabled'] = True
    game_state['question_locked'] = False
    game_state['correct_answer'] = questions_data['questions'][question_index]['correct']
    
    return jsonify({'success': True})

@app.route('/api/admin/lock-question', methods=['POST'])
def lock_question():
    """Lock the current question and reveal answer"""
    if game_state['current_question'] is None:
        return jsonify({'error': 'No active question'}), 400
    
    game_state['question_locked'] = True
    
    # Calculate points for teams
    current_q = questions_data['questions'][game_state['current_question']]
    points = current_q.get('points', 100)
    
    for team_number, team_data in game_state['teams'].items():
        if game_state['current_question'] in team_data['answers']:
            if team_data['answers'][game_state['current_question']] == game_state['correct_answer']:
                team_data['score'] += points
    
    return jsonify({'success': True, 'correct_answer': game_state['correct_answer']})

@app.route('/api/admin/reset-game', methods=['POST'])
def reset_game():
    """Reset the entire game"""
    game_state['current_question'] = None
    game_state['question_enabled'] = False
    game_state['question_locked'] = False
    game_state['teams'] = {}
    game_state['correct_answer'] = None
    
    return jsonify({'success': True})

@app.route('/api/team/submit-answer', methods=['POST'])
def submit_answer():
    """Submit team answer"""
    data = request.json
    team_number = data.get('team_number')
    answer = data.get('answer')
    
    if not game_state['question_enabled'] or game_state['question_locked']:
        return jsonify({'error': 'Question not available'}), 400
    
    if team_number not in game_state['teams']:
        return jsonify({'error': 'Invalid team'}), 400
    
    # Store answer
    game_state['teams'][team_number]['answers'][game_state['current_question']] = answer
    
    return jsonify({'success': True})

@app.route('/api/admin/upload-questions', methods=['POST'])
def upload_questions():
    """Upload new questions JSON file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.json'):
        return jsonify({'error': 'File must be a JSON file'}), 400
    
    try:
        # Parse and validate JSON
        content = file.read().decode('utf-8')
        new_questions = json.loads(content)
        
        # Validate structure
        if 'questions' not in new_questions:
            return jsonify({'error': 'Invalid format: missing "questions" key'}), 400
        
        if not isinstance(new_questions['questions'], list):
            return jsonify({'error': 'Invalid format: "questions" must be an array'}), 400
        
        # Validate each question
        for i, q in enumerate(new_questions['questions']):
            required_keys = ['question', 'answers', 'correct', 'points']
            for key in required_keys:
                if key not in q:
                    return jsonify({'error': f'Question {i+1} missing required key: {key}'}), 400
            
            if not all(opt in q['answers'] for opt in ['A', 'B', 'C', 'D']):
                return jsonify({'error': f'Question {i+1} must have answers A, B, C, D'}), 400
            
            if q['correct'] not in ['A', 'B', 'C', 'D']:
                return jsonify({'error': f'Question {i+1} has invalid correct answer'}), 400
        
        # Save the new questions
        save_questions(new_questions)
        
        # Reload questions in memory
        global questions_data
        questions_data = new_questions
        
        # Reset game state
        game_state['current_question'] = None
        game_state['question_enabled'] = False
        game_state['question_locked'] = False
        game_state['correct_answer'] = None
        
        return jsonify({
            'success': True, 
            'message': f'Successfully uploaded {len(new_questions["questions"])} questions'
        })
        
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Invalid JSON format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/api/admin/download-questions')
def download_questions():
    """Download current questions JSON file"""
    questions_file = os.path.join(os.path.dirname(__file__), 'questions.json')
    return send_file(questions_file, as_attachment=True, download_name='questions.json')

@app.route('/api/scoreboard')
def get_scoreboard():
    """Get current scoreboard"""
    scoreboard = [
        {
            'team_number': team_num,
            'name': team_data['name'],
            'score': team_data['score']
        }
        for team_num, team_data in game_state['teams'].items()
    ]
    scoreboard.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({'scoreboard': scoreboard})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
