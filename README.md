# AI Hedge Fund

An AI-powered hedge fund system that uses multiple AI agents to analyze stocks and make trading decisions. The system leverages various AI models to simulate different investment strategies and risk management approaches.

## Features

- Multiple AI analyst agents (e.g., Warren Buffett style analysis)
- Risk management system
- Portfolio management
- Backtesting capabilities
- Free financial data integration using Yahoo Finance
- Caching system for improved performance

## Installation

1. Clone the repository:
```bash
git clone https://github.com/simplesafe/ai-hedge-fund.git && cd ai-hedge-fund
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install .
pip install yfinance
```

## Usage

Run the hedge fund with a specific ticker:

```bash
python src/main.py --ticker AAPL
python src/main.py --ticker GOOG --show-agent-graph --show-reasoning --ollama 
```

Additional options:
- `--initial-cash`: Set initial cash position (default: 100000.0)
- `--margin-requirement`: Set margin requirement (default: 0.0)
- `--start-date`: Start date for analysis (YYYY-MM-DD)
- `--end-date`: End date for analysis (YYYY-MM-DD)
- `--show-reasoning`: Show reasoning from each agent
- `--show-agent-graph`: Show the agent graph
- `--ollama`: Use Ollama for local LLM inference

## Project Structure

```
src/
├── agents/         # AI agent implementations
├── data/          # Data models and caching
├── graph/         # Workflow graph definitions
├── llm/           # LLM model configurations
├── tools/         # Utility tools and API integrations
└── utils/         # Helper functions and utilities
```

## Data Sources

The project uses Yahoo Finance (yfinance) for free financial data, including:
- Historical price data
- Financial metrics
- Company information
- News

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
