# Swedish Language Learning App

A comprehensive Flask-based platform for learning Swedish, integrating advanced AI, VR/AR, blockchain certifications, and external integrations. Designed for immersive, personalized language education aligned with 2025 SLA research.

## Features

- **AI Tutors & Peer Networks**: Real-time AI conversations and collaborative learning via Socket.IO.
- **VR/AR Immersion**: WebXR environments for cultural and conversational practice.
- **Blockchain Certifications**: Ethereum-based NFT certificates for achievements.
- **Multi-Language Support**: Flask-Babel for Swedish, English, and Arabic interfaces.
- **Curriculum Adapters**: CEFR mapping to IB and Cambridge standards.
- **External Integrations**: Google Classroom sync and more.
- **Inclusive Design**: Voice-to-text for accessibility (WCAG 2.2 compliant).
- **Analytics & Tools**: Text processing, CEFR analysis, and progress tracking.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/swedish-language-app.git
   cd swedish-language-app
   ```

2. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

3. Set up environment variables (create `.env`):
   - `GROQ_API_KEY`: For AI chat (optional)
   - `INFURA_PROJECT_ID`: For blockchain (optional)
   - `GOOGLE_CLIENT_ID`: For Classroom API (optional)

4. Run the app:
   ```bash
   python run.py
   ```
   Or for batch processing:
   ```bash
   python run.py generate-gy25 input.txt output.md --book "Book Title" --options cefr=B1
   ```

## Usage

- Access the app at `http://localhost:5000`
- Teachers: Create assignments, view analytics
- Students: Engage in reading, writing, speaking exercises
- VR: Visit `/immersive/vr_environment`
- AI Chat: Use `/ai_chat`

## Testing

Run tests with pytest:
```bash
cd app
python -m pytest tests/
```

## Deployment

- **Docker**: Build and run with `Dockerfile`
- **Heroku**: Automated via GitHub Actions (set secrets: `HEROKU_API_KEY`, `HEROKU_EMAIL`, `HEROKU_APP_NAME`)
- **Local**: Use `run.py`

## Contributing

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Push and create a PR

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- High: AI tutors, VR/AR (completed)
- Medium: Blockchain, multi-language, integrations (completed)
- Low: Cultural modules, CI/CD, inclusivity (completed)

For questions, open an issue or contact the maintainers.