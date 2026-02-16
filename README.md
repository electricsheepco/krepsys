# Krepsys 🎒

> Self-hosted newsletter reader. Simple, fast, open source.

**Krepsys** (Lithuanian: "krepšys" = satchel) is a newsletter reader designed to declutter your email inbox. Get newsletters out of email and into a clean, focused reading experience.

## Features

- 📡 **RSS Support** - Subscribe to any RSS feed
- ✉️ **Newsletter Import** - Use with Kill the Newsletter
- 📖 **Clean Reader** - Distraction-free reading view
- 🔖 **Save for Later** - Mark articles to read later
- 🗄️ **Archive** - Keep inbox clean
- 🐳 **Docker Ready** - One-command deployment
- 🔓 **Open Source** - MIT License

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/krepsys.git
cd krepsys

# Start with Docker
docker-compose up -d

# Access at http://krepsys.local
```

## Documentation

- [Installation Guide](docs/installation.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Contributing](CONTRIBUTING.md)

## Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributors

Built with ❤️ by the open source community.
