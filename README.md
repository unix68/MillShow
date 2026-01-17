# MillShow - Who Wants to Be a Millionaire Game

A team-based quiz game inspired by "Who Wants to Be a Millionaire" where multiple teams compete simultaneously on the same questions.

## Features

- **Team Selection**: Teams choose their number (1-10) and get their own view
- **Game Master Control**: Hidden admin panel to control game flow
- **Real-time Updates**: All views update automatically via polling
- **Millionaire-Style UI**: Blue and gold themed interface matching the TV show
- **Score Tracking**: Live scoreboard showing team rankings
- **Simple Deployment**: No login required, URL-based access control

## Setup

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access the application:
- Team selection: http://localhost:5000
- Team view: http://localhost:5000/team/1 (replace 1 with team number)
- Admin panel: http://localhost:5000/admin-secret-path-12345

### Azure Deployment

#### Using Azure App Service

1. Create an Azure App Service (Python 3.11)

2. Configure environment variables:
```
SECRET_KEY=your-production-secret-key
ADMIN_URL=your-custom-admin-path
```

3. Deploy using Azure CLI:
```bash
az webapp up --name your-app-name --resource-group your-rg --runtime "PYTHON:3.11"
```

Or use the Azure Portal for deployment from GitHub/local Git.

## Configuration

Edit `config.py` to customize:
- `SECRET_KEY`: Secret key for Flask sessions
- `ADMIN_URL`: Custom path for admin panel (default: admin-secret-path-12345)
- `MAX_TEAMS`: Maximum number of teams (default: 10)

## Game Questions

### Editing Questions

You have two options to manage questions:

#### Option 1: Edit questions.json directly

Edit `questions.json` to customize your questions. Format:
```json
{
  "questions": [
    {
      "question": "Your question text?",
      "answers": {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      },
      "correct": "A",
      "points": 100
    }
  ]
}
```

A template file `questions-template.json` is provided as a starting point.

#### Option 2: Upload via Admin Panel

1. Open the admin panel
2. Click "📤 Upload Questions" button
3. Select your JSON file (must follow the format above)
4. The file will be validated and loaded immediately
5. You can also download the current questions using "📥 Download Questions"

**Note**: Uploading new questions will automatically reset the game state.

## How to Play

1. **Setup**: Game master opens admin panel, teams open their team views
2. **Present Question**: Game master shows question on TV/projector (e.g., PowerPoint)
3. **Enable Question**: Game master clicks "Enable" for the question
4. **Teams Answer**: Teams see the question and click their answer
5. **Lock & Reveal**: Game master clicks "Lock & Reveal Answer"
6. **Scoreboard**: Updated scores are shown to all teams

## Project Structure

```
MillShow/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── questions.json            # Current game questions
├── questions-template.json   # Template for creating custom questions
├── requirements.txt          # Python dependencies
├── requirements-prod.txt     # Production dependencies
├── startup.sh                # Azure startup script
├── Procfile                  # Deployment configuration
├── static/
│   └── style.css            # Millionaire-themed styles
└── templates/
    ├── index.html           # Team selection page
    ├── team.html            # Team game view
    └── admin.html           # Game master control panel
```

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Azure App Service
- **Storage**: In-memory (no database needed)

## License

This is a one-time use application created for entertainment purposes.
