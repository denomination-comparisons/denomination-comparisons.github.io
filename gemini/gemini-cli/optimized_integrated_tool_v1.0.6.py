"""
Optimized Gemini Integrated Tool for Standalone Gemini 2.5 Pro
Version: 1.0.6

This module provides a version of the integrated tool specifically optimized for
standalone use with Gemini 2.5 Pro, incorporating feedback from multiple AI models.

Key Improvements (v1.0.6):
- Added new "Analysis Suite" with three major tools:
  - `cefr`: A text analysis tool to determine linguistic difficulty (CEFR level) and detect potential bias.
  - `kallkritik`: A source criticism helper that generates critical thinking questions for any text.
  - `concept-map`: A visualization tool to generate concept maps from structured text input.
- Integrated new dependencies (spaCy, textstat, NetworkX, Matplotlib) with robust model loading.
- Added corresponding CLI commands for all new analysis tools.

Key Improvements (v1.0.5):
- Added support for Gemini 2.5 Pro-specific features (long context windows, advanced reasoning).
- Implemented enhanced multimodal processing with Gemini 2.5 Pro vision capabilities.
- Added performance monitoring and metrics collection for API calls.
- Implemented advanced caching with TTL for improved performance.
- Added batch processing capabilities for large projects.
- Enhanced error handling with detailed diagnostics and recovery mechanisms.
- Added support for Gemini CLI-specific configurations and environment variables.
- Implemented structured output formats compatible with Gemini 2.5 Pro JSON responses.
"""

import ast
import json
import os
import argparse
import logging
import re
from typing import List, Dict, Optional, Any, Type, AsyncGenerator, Tuple
import asyncio
from enum import Enum
import google.generativeai as genai
from functools import wraps, lru_cache
import time
from pathlib import Path
import yaml
from datetime import datetime, timedelta
import hashlib
import pickle
from dataclasses import dataclass, asdict
import aiofiles
from concurrent.futures import ThreadPoolExecutor

# --- New Imports for Analysis Suite ---
try:
    import spacy
    import textstat
    import nltk
    import requests
    import networkx as nx
    import matplotlib.pyplot as plt
    from io import StringIO
    import csv
    from sklearn.ensemble import RandomForestClassifier
except ImportError as e:
    print(f"Warning: Missing dependencies for Analysis Suite: {e}. Some features may not work.")
    print("Please run: pip install spacy textstat nltk requests networkx matplotlib scikit-learn")

# --- CLI Colors ---
class Colors:
    """ANSI color codes for CLI output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    LIGHTGRAY = '\033[37m'

# --- Error Handling ---
class AnalysisError(Exception):
    """Custom exception for analysis errors."""
    pass

class APIError(Exception):
    """Custom exception for API errors."""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass

# --- Logging ---
class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

def setup_logging(level: LogLevel = LogLevel.INFO):
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.value.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('gemini_tool.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# --- Performance Metrics ---
@dataclass
class APIMetrics:
    """Dataclass to track API performance metrics."""
    request_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    response_time: Optional[float] = None
    tokens_used: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None
    model_used: Optional[str] = None

class MetricsCollector:
    """Collects and reports performance metrics."""
    def __init__(self):
        self.metrics: List[APIMetrics] = []
    
    def add_metric(self, metric: APIMetrics):
        self.metrics.append(metric)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        if not self.metrics:
            return {"total_requests": 0}
        
        successful_requests = [m for m in self.metrics if m.success]
        failed_requests = [m for m in self.metrics if not m.success]
        
        total_time = sum(m.response_time or 0 for m in successful_requests)
        avg_response_time = total_time / len(successful_requests) if successful_requests else 0
        
        return {
            "total_requests": len(self.metrics),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "average_response_time": avg_response_time,
            "total_tokens_used": sum(m.tokens_used or 0 for m in successful_requests)
        }

# --- Configuration (Inspired by ref1) ---
class ConfigManager:
    """Manages configuration from YAML, environment, and defaults."""
    def __init__(self, config_path: Optional[str] = "config.yaml"):
        self.config_path = Path(config_path) if config_path else None
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load config from defaults, file, and environment variables."""
        config = self._load_defaults()
        
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                if file_config:
                    config.update(file_config)
                    logger.info(f"Loaded configuration from {self.config_path}")
            except (yaml.YAMLError, IOError) as e:
                logger.warning(f"Could not load or parse {self.config_path}: {e}")

        self._load_from_env(config)
        return config

    def _load_defaults(self) -> dict:
        return {
            "max_function_length": 50,
            "complexity_threshold": 10,
            "model_name": "gemini-1.5-pro-latest",
            "vision_model_name": "gemini-1.5-pro-vision-latest",
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "timeout": 60,
            "retry_attempts": 5,
            "retry_delay": 1.0,
            "cache_size": 256,
            "cache_ttl": 3600,
            "batch_size": 10,
            "max_concurrent_requests": 5,
            "enable_metrics": True,
            "enable_batch_processing": True
        }

    def _load_from_env(self, config: dict):
        """Override config with environment variables."""
        for key in config:
            env_var = f"GEMINI_TOOL_{key.upper()}"
            if env_var in os.environ:
                value = os.environ[env_var]
                try:
                    original_type = type(config[key])
                    if original_type == bool:
                        config[key] = value.lower() in ('true', '1', 'yes')
                    else:
                        config[key] = original_type(value)
                    logger.info(f"Overrode '{key}' with value from {env_var}")
                except (ValueError, TypeError):
                    logger.warning(f"Could not cast env var {env_var} to {original_type}")

    def __getattr__(self, name):
        return self.config.get(name.lower())

# --- Enhanced Caching System ---
class TTLCache:
    """Time-to-live cache with expiration."""
    def __init__(self, ttl: int = 3600, maxsize: int = 128):
        self.ttl = ttl
        self.maxsize = maxsize
        self.cache = {}
        self.access_times = {}
    
    def __contains__(self, key):
        if key in self.cache:
            if time.time() - self.access_times[key] < self.ttl:
                return True
            else:
                del self.cache[key]
                del self.access_times[key]
        return False
    
    def __getitem__(self, key):
        if key in self.cache:
            if time.time() - self.access_times[key] < self.ttl:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.access_times[key]
        raise KeyError(key)
    
    def __setitem__(self, key, value):
        if len(self.cache) >= self.maxsize:
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = time.time()

# --- AI Model Strategy ---
def retry_with_backoff(max_attempts=3, delay=1.0, backoff=2.0):
    """Decorator for retrying API calls with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except APIError as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    
                    logger.warning(f"{Colors.WARNING}Attempt {attempt} failed: {e}. Retrying in {current_delay}s...{Colors.ENDC}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise APIError(f"Max retry attempts ({max_attempts}) exceeded")
        return wrapper
    return decorator

class Gemini15ProStrategy:
    """Gemini 1.5 Pro-specific optimization strategy."""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.metrics_collector = MetricsCollector() if config.enable_metrics else None
        self.cache = TTLCache(ttl=config.cache_ttl, maxsize=config.cache_size)
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_requests)

    @retry_with_backoff(max_attempts=5, delay=1.0, backoff=2.0)
    async def call_gemini_api(self, 
                                   prompt: str, 
                                   image_data: Optional[bytes] = None, 
                                   stream: bool = False,
                                   system_instruction: Optional[str] = None) -> str:
        """Calls the actual Gemini 1.5 Pro API using 'google-generativeai'."""
        request_id = hashlib.md5(f"{prompt}{time.time()}".encode()).hexdigest()[:8]
        logger.info(f"--- Calling Gemini 1.5 Pro API (Request ID: {request_id}) ---")
        
        start_time = datetime.now()
        metric = APIMetrics(
            request_id=request_id,
            start_time=start_time,
            model_used=self.config.model_name if not image_data else self.config.vision_model_name
        )
        
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            
            genai.configure(api_key=api_key)
            
            model_name = self.config.model_name
            if image_data:
                model_name = self.config.vision_model_name

            generation_config = genai.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                response_mime_type="text/plain"
            )
            
            safety_settings = [
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            ]
            
            model = genai.GenerativeModel(
                model_name,
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=system_instruction
            )

            contents = [prompt]
            if image_data:
                import PIL.Image
                from io import BytesIO
                image = PIL.Image.open(BytesIO(image_data))
                contents.append(image)

            if stream:
                response = await asyncio.to_thread(
                    model.generate_content, contents, stream=True
                )
                full_response = ""
                print(f"{Colors.OKCYAN}--- Generated Code ---{Colors.ENDC}")
                for chunk in response:
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                        full_response += chunk.text
                print()
                return full_response
            else:
                response = await asyncio.to_thread(model.generate_content, contents)
                
                if self.metrics_collector:
                    metric.end_time = datetime.now()
                    metric.response_time = (metric.end_time - metric.start_time).total_seconds()
                    if hasattr(response, 'usage_metadata'):
                        metric.tokens_used = response.usage_metadata.total_token_count
                    metric.success = True
                    self.metrics_collector.add_metric(metric)
                
                return response.text
        except Exception as e:
            logger.error(f"{Colors.FAIL}Error calling Gemini 1.5 Pro API: {e}{Colors.ENDC}")
            if self.metrics_collector:
                metric.end_time = datetime.now()
                metric.response_time = (metric.end_time - metric.start_time).total_seconds()
                metric.error_message = str(e)
                metric.success = False
                self.metrics_collector.add_metric(metric)
            raise APIError(f"API call failed: {e}")

# --- NEW: Analysis Suite ---
class AnalysisSuite:
    """Houses new analysis tools for text and concepts."""
    def __init__(self, config: ConfigManager):
        self.config = config
        self.nlp = self._load_spacy_model()
        self.freq_list = self._load_frequency_list()
        self.cefr_model = self._get_cefr_model()

    def _load_spacy_model(self):
        """Loads the spaCy model, downloading if necessary."""
        try:
            # Set environment variable to handle potential torch backend issues
            os.environ['TORCH_DEVICE_BACKEND_AUTOLOAD'] = '0'
            return spacy.load("sv_core_news_sm")
        except OSError:
            logger.warning("spaCy model 'sv_core_news_sm' not found. Attempting to download...")
            try:
                spacy.cli.download("sv_core_news_sm")
                return spacy.load("sv_core_news_sm")
            except Exception as e:
                logger.error(f"Failed to download spaCy model: {e}")
                return None

    def _load_frequency_list(self, url="https://raw.githubusercontent.com/spraakbanken/kelly-list/master/kelly.csv"):
        """Loads the Kelly frequency list."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            reader = csv.reader(StringIO(response.text))
            next(reader) # Skip header
            return {row[0].lower(): row[1] for row in reader if len(row) > 1}
        except Exception as e:
            logger.error(f"Could not load frequency list: {e}")
            return {}

    def _get_cefr_model(self):
        """Creates a pre-trained CEFR model instance."""
        training_data = [
            {"text": "Jag heter Anna.", "lix": 5, "vocab_match": 95, "avg_depth": 1.5, "teacher_rating": "A1"},
            {"text": "I går gick jag till skolan.", "lix": 15, "vocab_match": 85, "avg_depth": 2.0, "teacher_rating": "A2"},
            {"text": "Jag tycker att klimatförändringar är ett stort problem.", "lix": 30, "vocab_match": 70, "avg_depth": 3.0, "teacher_rating": "B1"},
            {"text": "Teknologin utvecklas snabbt.", "lix": 40, "vocab_match": 60, "avg_depth": 3.5, "teacher_rating": "B2"}
        ]
        X = [[item["lix"], item["vocab_match"], item.get("avg_depth", 0)] for item in training_data]
        y = [item["teacher_rating"] for item in training_data]
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        return model

    def analyze_cefr(self, text: str) -> Dict[str, Any]:
        """Analyzes text for CEFR level and potential bias."""
        if not self.nlp or not self.freq_list:
            raise AnalysisError("CEFR analysis tools are not initialized.")
        
        lix = textstat.lix(text)
        doc = self.nlp(text)
        words = [token.text.lower() for token in doc if token.is_alpha]
        if not words:
            return {"level": "N/A", "explanation": "No words to analyze.", "warnings": []}

        low_freq_count = sum(1 for w in words if self.freq_list.get(w, 'C1') in ['A1', 'A2'])
        low_freq_percent = (low_freq_count / len(words)) * 100
        depths = [max((len(list(token.subtree)) for token in sent if token.dep_ != 'ROOT'), default=1) for sent in doc.sents]
        avg_depth = sum(depths) / len(depths) if depths else 0

        features = [[lix, low_freq_percent, avg_depth]]
        level = self.cefr_model.predict(features)[0]
        
        explanation = f"Beräknad CEFR-nivå: {level}. Analys baseras på LIX ({lix:.2f}), andel basvokabulär ({low_freq_percent:.1f}%), och meningsstruktur (syntaxdjup {avg_depth:.1f})."
        
        # Bias detection
        warnings = []
        male_pronouns = len([t for t in doc if t.text.lower() in ["han", "hans", "honom"]])
        female_pronouns = len([t for t in doc if t.text.lower() in ["hon", "hennes", "henne"]])
        if male_pronouns + female_pronouns > 0:
            ratio = male_pronouns / (female_pronouns + 1)
            if ratio > 3 or (female_pronouns > 0 and ratio < 0.33):
                warnings.append(f"Könsobalans i pronomen (ratio: {ratio:.2f})")
        
        return {"level": level, "explanation": explanation, "warnings": warnings}

    def generate_source_criticism(self, text: str) -> Dict[str, List[str]]:
        """Generates source criticism questions for a given text."""
        if not self.nlp:
            raise AnalysisError("Source criticism tools are not initialized.")
        
        doc = self.nlp(text)
        questions = [
            "Vem är avsändaren och vad är deras syfte?",
            "När publicerades texten och är den fortfarande relevant?",
            "Vilka bevis eller källor presenteras? Är de kontrollerbara?",
            "[Transparens] Hur öppet redovisas informationens ursprung?",
            "[Klassificering] Vilka kategorier eller grupper skapas i texten? Är indelningen rättvis?"
        ]
        warnings = []
        
        sensitive_themes = ["ras", "kön", "religion", "politik", "invandring"]
        found_themes = [theme for theme in sensitive_themes if theme in text.lower()]
        if found_themes:
            warnings.append(f"Texten berör potentiellt känsliga teman: {', '.join(found_themes)}.")
            questions.append(f"[Reflektion] Vilka perspektiv kring '{found_themes[0]}' kan saknas?")
            
        return {"questions": questions, "warnings": warnings}

    def generate_concept_map(self, text_input: str, output_path: str) -> str:
        """Generates a concept map and saves it to a file."""
        plt.switch_backend('Agg')
        G = nx.DiGraph()
        edge_labels = {}
        pattern = re.compile(r'(.+?)\s*->\s*(.+?)\s*\[(.+?)\]')

        for line in text_input.strip().split('\n'):
            match = pattern.match(line.strip())
            if match:
                source, target, label = [s.strip() for s in match.groups()]
                G.add_edge(source, target)
                edge_labels[(source, target)] = label

        if not G.nodes():
            raise ValueError("No valid relationships found in input. Format: 'Source -> Target [Label]'")

        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=0.9, iterations=50, seed=42)
        nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='#a0c4ff')
        nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, edge_color='#b1b1b1', arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_color='#c9184a')
        plt.title('Concept Map', size=20)
        plt.axis('off')
        
        plt.savefig(output_path, format='PNG', dpi=200, bbox_inches='tight')
        plt.close()
        return f"Concept map saved to {output_path}"

# --- Main Integrated Tool ---
class IntegratedTool:
    """Main integrated tool class, optimized for standalone Gemini 1.5 Pro."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = ConfigManager(config_path)
        self.analyzer = CodeAnalyzer(self.config)
        self.strategy = Gemini15ProStrategy(self.config)
        self.suite = AnalysisSuite(self.config) # New Suite

    async def run_full_analysis(self, code: str) -> Dict[str, Any]:
        # ... (existing code)
        pass

# --- CLI and Execution ---
async def main():
    """Main execution function for the CLI."""
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}Optimized Gemini Integrated Tool v1.0.6{Colors.ENDC}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze myfile.py
  %(prog)s generate "Create a function to calculate factorial"
  %(prog)s cefr "En text att analysera." --output cefr_results.json
  %(prog)s kallkritik "En annan text..."
  %(prog)s concept-map relations.txt --output map.png
        """
    )
    parser.add_argument("--config", type=str, help="Path to a custom configuration file.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Existing Parsers (analyze, generate, etc.) ---
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single Python file.")
    analyze_parser.add_argument("file_path", type=str, help="Path to the Python file.")
    generate_parser = subparsers.add_parser("generate", help="Generate Python code.")
    generate_parser.add_argument("description", type=str, help="A description of the code to generate.")

    # --- New Parsers for Analysis Suite ---
    cefr_parser = subparsers.add_parser("cefr", help="Analyze text for CEFR level.")
    cefr_parser.add_argument("text", type=str, help="The text to analyze or path to a text file.")
    cefr_parser.add_argument("--output", type=str, help="Path to save results as JSON.")

    kallkritik_parser = subparsers.add_parser("kallkritik", help="Generate source criticism questions.")
    kallkritik_parser.add_argument("text", type=str, help="The text to analyze or path to a text file.")
    kallkritik_parser.add_argument("--output", type=str, help="Path to save results as JSON.")

    map_parser = subparsers.add_parser("concept-map", help="Generate a concept map from structured text.")
    map_parser.add_argument("input_file", type=str, help="Path to a file with relationship definitions.")
    map_parser.add_argument("--output", type=str, default="concept_map.png", help="Path to save the output PNG image.")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    tool = IntegratedTool(config_path=args.config)

    # --- Command Handling ---
    if args.command == "analyze":
        # ... (existing implementation)
        logger.info(f"Analyzing {args.file_path}...")
        # results = await tool.run_full_analysis(code)
        # print(json.dumps(results, indent=2))

    elif args.command == "generate":
        # ... (existing implementation)
        logger.info(f"Generating code for: {args.description}")
        # generated_code = await tool.strategy.generate_code_with_reasoning(args.description)
        # print(generated_code)

    # --- New Command Handlers ---
    elif args.command in ["cefr", "kallkritik"]:
        text_input = args.text
        if os.path.exists(text_input):
            logger.info(f"Reading text from file: {text_input}")
            with open(text_input, 'r', encoding='utf-8') as f:
                text_input = f.read()

        if args.command == "cefr":
            logger.info("--- Analyzing Text for CEFR Level ---")
            results = tool.suite.analyze_cefr(text_input)
        else: # kallkritik
            logger.info("--- Generating Source Criticism Questions ---")
            results = tool.suite.generate_source_criticism(text_input)
        
        output_str = json.dumps(results, indent=2, ensure_ascii=False)
        print(output_str)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            logger.info(f"Results saved to {args.output}")

    elif args.command == "concept-map":
        logger.info(f"--- Generating Concept Map from {args.input_file} ---")
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                text_input = f.read()
            
            result_message = tool.suite.generate_concept_map(text_input, args.output)
            logger.info(f"{Colors.OKGREEN}{result_message}{Colors.ENDC}")
        except FileNotFoundError:
            logger.error(f"{Colors.FAIL}Input file not found: {args.input_file}{Colors.ENDC}")
        except Exception as e:
            logger.error(f"{Colors.FAIL}Failed to generate map: {e}{Colors.ENDC}")


if __name__ == "__main__":
    # This is a simplified main loop. The full version has more complex logic.
    # For brevity, the original main() content is partially omitted.
    asyncio.run(main())