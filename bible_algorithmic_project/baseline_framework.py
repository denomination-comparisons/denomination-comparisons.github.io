# bible_algorithmic_project - Baseline Framework v0.1.0
# Date: 2025-10-25
# Production-ready framework with multi-dimensional analysis, plugin architecture, and advanced features

import json
import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# spaCy integration for v0.1.0 - Enhanced with better error handling and logging
SPACY_AVAILABLE = False
nlp = None

try:
    import spacy
    SPACY_AVAILABLE = True
    logging.info("spaCy imported successfully")

    # Try to load the model with multiple fallback strategies
    try:
        # First try the standard model
        nlp = spacy.load("en_core_web_sm")
        logging.info("spaCy en_core_web_sm model loaded successfully")
    except (OSError, RuntimeError) as model_error:
        logging.warning(f"Standard model failed: {model_error}")
        try:
            # Try loading with disabled GPU/accelerators
            import os
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
            os.environ["TORCH_DEVICE_BACKEND_AUTOLOAD"] = "0"
            nlp = spacy.load("en_core_web_sm", disable=["gpu"])
            logging.info("spaCy model loaded with GPU disabled")
        except Exception as fallback_error:
            logging.warning(f"Fallback loading also failed: {fallback_error}")
            try:
                # Try a smaller model as last resort
                nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "gpu"])
                logging.info("spaCy model loaded with minimal components")
            except Exception as minimal_error:
                logging.error(f"Minimal model loading failed: {minimal_error}")
                SPACY_AVAILABLE = False
                nlp = None

except ImportError as import_error:
    logging.error(f"spaCy import failed: {import_error}")
    logging.info("Install spaCy with: pip install spacy")
    logging.info("Then download model with: python -m spacy download en_core_web_sm")
    SPACY_AVAILABLE = False
except Exception as general_error:
    logging.error(f"Unexpected spaCy loading error: {general_error}")
    SPACY_AVAILABLE = False

if SPACY_AVAILABLE and nlp:
    logging.info("SUCCESS: spaCy NLP pipeline ready for advanced analysis")
    # Test spaCy functionality
    try:
        test_doc = nlp("The Word was with God.")
        test_tokens = [token.text for token in test_doc]
        test_lemmas = [token.lemma_ for token in test_doc]
        test_pos = [token.pos_ for token in test_doc]
        logging.info(f"spaCy test successful: {len(test_tokens)} tokens, {len(set(test_lemmas))} unique lemmas, POS tags: {test_pos[:3]}...")
    except Exception as test_error:
        logging.error(f"spaCy test failed: {test_error}")
        SPACY_AVAILABLE = False
        nlp = None
else:
    logging.warning("spaCy not available - framework will use basic text processing")
    logging.info("To enable full NLP features, resolve spaCy installation issues above")

# Version control
__version__ = "0.1.0"

class AnalysisDimension(Enum):
    """10 core dimensions for v0.1.0"""
    LEXICAL = "lexical"              # Language/word analysis
    THEMATIC = "thematic"             # Theological themes
    STRUCTURAL = "structural"         # Sentence/clause structure
    CHRISTOLOGICAL = "christological" # Christ-focused content
    CROSS_REFERENCE = "cross_reference" # Connections to other passages
    LITERARY = "literary"             # Literary devices
    ETHICAL = "ethical"               # Moral/ethical content
    TEMPORAL = "temporal"             # Time-based patterns and sequences
    ESCHATOLOGICAL = "eschatological" # End-times themes and prophecy
    HISTORICAL = "historical"         # Historical and cultural context



@dataclass
class BiblicalPassage:
    """Represents a biblical passage with enhanced metadata and preprocessing caching"""
    reference: str
    text: str
    version: str = "ESV"
    testament: str = "New"
    book: str = ""
    chapter: int = 0
    verse: int = 0
    # Enhanced metadata fields (v0.1.0)
    keywords: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)
    word_count: int = 0
    unique_word_count: int = 0
    lexical_diversity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Preprocessing cache (v0.0.6-7)
    _preprocessing_cache: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        """Auto-populate metadata fields after initialization"""
        self.populate_metadata()

    def get_cached_words(self) -> List[str]:
        """Get cached word list for performance"""
        if 'words' not in self._preprocessing_cache:
            self._preprocessing_cache['words'] = self.text.split()
        return self._preprocessing_cache['words']

    def get_cached_word_freq(self) -> Dict[str, int]:
        """Get cached word frequency dictionary"""
        if 'word_freq' not in self._preprocessing_cache:
            words = self.get_cached_words()
            word_freq = {}
            for word in words:
                word_lower = word.lower()
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            self._preprocessing_cache['word_freq'] = word_freq
        return self._preprocessing_cache['word_freq']

    def get_cached_text_lower(self) -> str:
        """Get cached lowercase text"""
        if 'text_lower' not in self._preprocessing_cache:
            self._preprocessing_cache['text_lower'] = self.text.lower()
        return self._preprocessing_cache['text_lower']

    def get_synonym_expanded_keywords(self) -> List[str]:
        """Get keywords expanded with synonyms"""
        if 'expanded_keywords' not in self._preprocessing_cache:
            synonym_dict = SynonymDictionary()
            self._preprocessing_cache['expanded_keywords'] = synonym_dict.expand_keywords(self.keywords)
        return self._preprocessing_cache['expanded_keywords']

    def get_spacy_doc(self):
        """Get cached spaCy Doc object for advanced NLP processing"""
        if not SPACY_AVAILABLE or nlp is None:
            return None

        if 'spacy_doc' not in self._preprocessing_cache:
            self._preprocessing_cache['spacy_doc'] = nlp(self.text)
        return self._preprocessing_cache['spacy_doc']

    def get_lemmas(self) -> List[str]:
        """Get lemmatized words using spaCy"""
        doc = self.get_spacy_doc()
        if doc is None:
            # Fallback to simple lemmatization
            return [word.lower() for word in self.get_cached_words()]
        return [token.lemma_.lower() for token in doc]

    def get_pos_tags(self) -> List[str]:
        """Get part-of-speech tags using spaCy"""
        doc = self.get_spacy_doc()
        if doc is None:
            return []
        return [token.pos_ for token in doc]

    def get_named_entities(self) -> List[Dict[str, Any]]:
        """Get named entities using spaCy NER"""
        doc = self.get_spacy_doc()
        if doc is None:
            return []
        return [{"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
                for ent in doc.ents]

    def populate_metadata(self):
        """Populate numerical metadata fields with caching"""
        words = self.get_cached_words()
        word_freq = self.get_cached_word_freq()

        self.word_count = len(words)
        unique_words = set(word_freq.keys())
        self.unique_word_count = len(unique_words)
        self.lexical_diversity = self.unique_word_count / self.word_count if self.word_count > 0 else 0.0

        # Basic keyword extraction if not provided
        if not self.keywords:
            common_keywords = ["god", "jesus", "spirit", "love", "faith", "lord", "heaven", "earth"]
            text_lower = self.get_cached_text_lower()
            self.keywords = [kw for kw in common_keywords if kw in text_lower]

class BibleLoader:
    """Loader for biblical corpora in various formats (JSON, USFM, etc.)"""

    def __init__(self):
        self.books = {}  # book_name -> List[BiblicalPassage]
        self.passages = []  # All passages in order
        self.book_order = []  # Canonical book order

    def load_from_json(self, filepath: str):
        """Load Bible from JSON format"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            passages = []
            for book_data in data.get('books', []):
                book_name = book_data.get('name', '')
                book_abbrev = book_data.get('abbreviation', '')
                testament = book_data.get('testament', 'New')

                for chapter_data in book_data.get('chapters', []):
                    chapter_num = chapter_data.get('number', 0)

                    for verse_data in chapter_data.get('verses', []):
                        verse_num = verse_data.get('number', 0)
                        text = verse_data.get('text', '')

                        # Create reference
                        reference = f"{book_abbrev} {chapter_num}:{verse_num}"

                        passage = BiblicalPassage(
                            reference=reference,
                            text=text,
                            version=data.get('version', 'Unknown'),
                            testament=testament,
                            book=book_name,
                            chapter=chapter_num,
                            verse=verse_num
                        )

                        passages.append(passage)

            self.passages = passages
            self._organize_by_book()
            print(f"Loaded {len(passages)} passages from JSON")
            return passages

        except FileNotFoundError:
            print(f"Bible file not found: {filepath}")
            return []
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in Bible file: {e}")
            return []

    def load_from_usfm(self, filepath: str):
        """Load Bible from USFM (Unified Standard Format Markers) format"""
        # Basic USFM parser - can be extended for full USFM support
        try:
            passages = []
            current_book = ""
            current_chapter = 0
            current_verse = 0
            current_text = ""
            testament = "Old"  # Default

            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()

                    # Book marker
                    if line.startswith('\\id ') or line.startswith('\\h '):
                        if current_text and current_book:
                            # Save previous passage
                            reference = f"{current_book} {current_chapter}:{current_verse}"
                            passage = BiblicalPassage(
                                reference=reference,
                                text=current_text.strip(),
                                version="USFM",
                                testament=testament,
                                book=current_book,
                                chapter=current_chapter,
                                verse=current_verse
                            )
                            passages.append(passage)

                        # Start new book
                        parts = line.split()
                        if len(parts) > 1:
                            current_book = parts[1]
                            # Determine testament
                            old_testament_books = [
                                'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT', '1SA', '2SA',
                                '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST', 'JOB', 'PSA', 'PRO',
                                'ECC', 'SNG', 'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS', 'JOL', 'AMO',
                                'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL'
                            ]
                            testament = "Old" if current_book.upper() in old_testament_books else "New"
                        current_text = ""

                    # Chapter marker
                    elif line.startswith('\\c '):
                        parts = line.split()
                        if len(parts) > 1:
                            try:
                                current_chapter = int(parts[1])
                            except ValueError:
                                current_chapter = 0

                    # Verse marker
                    elif line.startswith('\\v '):
                        # Save previous verse if exists
                        if current_text and current_verse > 0:
                            reference = f"{current_book} {current_chapter}:{current_verse}"
                            passage = BiblicalPassage(
                                reference=reference,
                                text=current_text.strip(),
                                version="USFM",
                                testament=testament,
                                book=current_book,
                                chapter=current_chapter,
                                verse=current_verse
                            )
                            passages.append(passage)

                        # Start new verse
                        parts = line.split(' ', 2)
                        if len(parts) > 1:
                            try:
                                current_verse = int(parts[1])
                            except ValueError:
                                current_verse = 0
                        current_text = ' '.join(parts[2:]) if len(parts) > 2 else ""

                    # Text continuation
                    elif line and not line.startswith('\\'):
                        current_text += ' ' + line

            # Save final passage
            if current_text and current_book:
                reference = f"{current_book} {current_chapter}:{current_verse}"
                passage = BiblicalPassage(
                    reference=reference,
                    text=current_text.strip(),
                    version="USFM",
                    testament=testament,
                    book=current_book,
                    chapter=current_chapter,
                    verse=current_verse
                )
                passages.append(passage)

            self.passages = passages
            self._organize_by_book()
            print(f"Loaded {len(passages)} passages from USFM")
            return passages

        except FileNotFoundError:
            print(f"USFM file not found: {filepath}")
            return []
        except Exception as e:
            print(f"Error parsing USFM file: {e}")
            return []

    def _organize_by_book(self):
        """Organize passages by book"""
        self.books = {}
        for passage in self.passages:
            if passage.book not in self.books:
                self.books[passage.book] = []
            self.books[passage.book].append(passage)

        # Set canonical order
        canonical_order = [
            # Old Testament
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth',
            '1 Samuel', '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther',
            'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Lamentations',
            'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk',
            'Zephaniah', 'Haggai', 'Zechariah', 'Malachi',
            # New Testament
            'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians', '2 Corinthians', 'Galatians',
            'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy',
            'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation'
        ]

        self.book_order = [book for book in canonical_order if book in self.books]

    def get_passage(self, reference: str):
        """Get a specific passage by reference"""
        for passage in self.passages:
            if passage.reference == reference:
                return passage
        return None

    def get_book(self, book_name: str):
        """Get all passages from a specific book"""
        return self.books.get(book_name, [])

    def get_chapter(self, book_name: str, chapter_num: int):
        """Get all passages from a specific chapter"""
        book_passages = self.get_book(book_name)
        return [p for p in book_passages if p.chapter == chapter_num]

    def search_text(self, query: str, case_sensitive: bool = False):
        """Search for passages containing specific text"""
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(re.escape(query), flags)

        results = []
        for passage in self.passages:
            if pattern.search(passage.text):
                results.append(passage)

        return results

    def get_statistics(self):
        """Get statistics about the loaded corpus"""
        if not self.passages:
            return {"total_passages": 0}

        total_words = sum(len(p.get_cached_words()) for p in self.passages)
        total_unique_words = len(set(word.lower() for p in self.passages for word in p.get_cached_words()))

        book_stats = {}
        for book, passages in self.books.items():
            book_stats[book] = {
                "passages": len(passages),
                "chapters": len(set(p.chapter for p in passages)),
                "verses": len(passages),
                "words": sum(len(p.get_cached_words()) for p in passages)
            }

        return {
            "total_passages": len(self.passages),
            "total_books": len(self.books),
            "total_words": total_words,
            "unique_words": total_unique_words,
            "lexical_diversity": total_unique_words / total_words if total_words > 0 else 0,
            "books": book_stats,
            "testament_breakdown": {
                "old_testament": len([p for p in self.passages if p.testament == "Old"]),
                "new_testament": len([p for p in self.passages if p.testament == "New"])
            }
        }

@dataclass
class LinkedPassage:
    """Represents a conceptual link (a graph edge)"""
    reference: str
    relationship: str  # e.g., 'narrative_instance', 'thematic', 'reiteration'
    insight: str

@dataclass
class DimensionalAnalysis:
    """Result from a dimensional analysis"""
    dimension: AnalysisDimension
    findings: Dict[str, Any]
    insights: List[str]
    confidence: float = 1.0
    links: List[LinkedPassage] = field(default_factory=list)

@dataclass
class MultiDimensionalResult:
    """Result from multi-dimensional analysis"""
    passage: BiblicalPassage
    dimension_results: Dict[AnalysisDimension, DimensionalAnalysis]
    synthesis: str
    multiplication_factor: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_total_insights(self) -> int:
        return sum(len(result.insights) for result in self.dimension_results.values())

    def get_total_findings(self) -> int:
        return sum(len(result.findings) for result in self.dimension_results.values())

    def get_average_confidence(self) -> float:
        if not self.dimension_results:
            return 0.0
        return sum(result.confidence for result in self.dimension_results.values()) / len(self.dimension_results)

@dataclass
class AlgorithmPlugin:
    """Plugin metadata for algorithm registration"""
    name: str
    function: callable
    category: str = "general"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    version: str = "1.0"
    author: str = "system"
    tags: List[str] = field(default_factory=list)

@dataclass
class ValidationRule:
    """External validation rule definition"""
    name: str
    description: str
    condition: str  # Python expression to evaluate
    severity: str = "medium"  # low, medium, high, critical
    category: str = "general"
    enabled: bool = True
    message_template: str = ""
    suggested_fix: str = ""

class SynonymDictionary:
    """Enhanced synonym dictionary for biblical keyword matching"""

    def __init__(self):
        self.synonym_map = {}
        self.reverse_map = {}  # word -> canonical form
        self.load_biblical_synonyms()

    def load_biblical_synonyms(self):
        """Load biblical synonym mappings"""
        biblical_synonyms = {
            # Creation synonyms
            "create": ["make", "form", "fashion", "establish", "bring forth", "produce"],
            "beginning": ["start", "origin", "commencement", "inception", "genesis"],

            # Salvation synonyms
            "save": ["deliver", "rescue", "redeem", "liberate", "free"],
            "salvation": ["deliverance", "redemption", "rescue", "liberation"],

            # Kingdom synonyms
            "kingdom": ["realm", "domain", "empire", "sovereignty", "rule"],
            "king": ["ruler", "sovereign", "monarch", "lord", "prince"],

            # Love synonyms
            "love": ["affection", "devotion", "passion", "tenderness", "compassion"],
            "beloved": ["dear", "cherished", "precious", "darling"],

            # Faith synonyms
            "faith": ["belief", "trust", "confidence", "assurance", "conviction"],
            "believe": ["trust", "have faith", "accept", "credit"],

            # Holiness synonyms
            "holy": ["sacred", "divine", "consecrated", "sanctified", "pure"],
            "righteous": ["just", "upright", "moral", "virtuous", "godly"],

            # Wisdom synonyms
            "wise": ["prudent", "sagacious", "discerning", "insightful", "judicious"],
            "wisdom": ["understanding", "knowledge", "discernment", "insight"],

            # Justice synonyms
            "justice": ["fairness", "righteousness", "equity", "impartiality"],
            "judge": ["adjudicate", "decide", "determine", "rule"],

            # Christological synonyms
            "christ": ["messiah", "anointed", "savior", "redeemer"],
            "jesus": ["christ", "savior", "lord", "master"],
            "son of god": ["god's son", "divine son", "heavenly son"],
            "son of man": ["human son", "man's son", "mortal son"],

            # Eschatological synonyms
            "end": ["conclusion", "termination", "finish", "close"],
            "judgment": ["condemnation", "verdict", "sentence", "decision"],
            "heaven": ["paradise", "celestial realm", "eternal home"],
            "earth": ["world", "land", "ground", "terra firma"]
        }

        for canonical, synonyms in biblical_synonyms.items():
            self.synonym_map[canonical] = synonyms
            for synonym in synonyms:
                self.reverse_map[synonym] = canonical

    def get_synonyms(self, word: str) -> List[str]:
        """Get all synonyms for a word"""
        canonical = self.reverse_map.get(word.lower(), word.lower())
        return self.synonym_map.get(canonical, [])

    def get_canonical_form(self, word: str) -> str:
        """Get canonical form of a word"""
        return self.reverse_map.get(word.lower(), word.lower())

    def expand_keywords(self, keywords: List[str]) -> List[str]:
        """Expand keywords with their synonyms"""
        expanded = set(keywords)
        for keyword in keywords:
            expanded.update(self.get_synonyms(keyword))
        return list(expanded)

    def find_synonym_matches(self, text: str, keywords: List[str]) -> Dict[str, List[str]]:
        """Find synonym matches in text"""
        text_lower = text.lower()
        matches = {}

        for keyword in keywords:
            canonical = self.get_canonical_form(keyword)
            all_forms = [canonical] + self.get_synonyms(keyword)

            found_matches = [form for form in all_forms if form in text_lower]
            if found_matches:
                matches[keyword] = found_matches

        return matches

@dataclass
class AlgorithmicResult:
    """Result from an algorithmic analysis"""
    algorithm_name: str
    input_passage: BiblicalPassage
    findings: Dict[str, Any]
    insights: List[str]
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    links: List[LinkedPassage] = field(default_factory=list)

class AlgorithmicFramework:
    """Base framework for biblical algorithmic processing with plugin architecture"""

    def __init__(self):
        self.algorithms = {}  # name -> function mapping
        self.plugins = {}     # name -> AlgorithmPlugin mapping
        self.passage_cache = {}
        self.categories = {}  # category -> list of algorithm names

    def register_algorithm(self, name: str, algorithm_func, category: str = "general",
                          description: str = "", dependencies: List[str] = None,
                          version: str = "1.0", author: str = "system", tags: List[str] = None):
        """Register an algorithmic function as a plugin"""
        plugin = AlgorithmPlugin(
            name=name,
            function=algorithm_func,
            category=category,
            description=description,
            dependencies=dependencies or [],
            version=version,
            author=author,
            tags=tags or []
        )

        self.algorithms[name] = algorithm_func
        self.plugins[name] = plugin

        # Update category index
        if category not in self.categories:
            self.categories[category] = []
        if name not in self.categories[category]:
            self.categories[category].append(name)

    def unregister_algorithm(self, name: str):
        """Unregister an algorithm plugin"""
        if name in self.plugins:
            category = self.plugins[name].category
            if category in self.categories and name in self.categories[category]:
                self.categories[category].remove(name)
            del self.plugins[name]
        if name in self.algorithms:
            del self.algorithms[name]

    def get_plugin_info(self, name: str) -> Optional[AlgorithmPlugin]:
        """Get plugin metadata"""
        return self.plugins.get(name)

    def list_plugins(self, category: str = None) -> List[AlgorithmPlugin]:
        """List all plugins or plugins in a specific category"""
        if category:
            plugin_names = self.categories.get(category, [])
            return [self.plugins[name] for name in plugin_names if name in self.plugins]
        return list(self.plugins.values())

    def get_plugin_categories(self) -> List[str]:
        """Get all plugin categories"""
        return list(self.categories.keys())

    def check_dependencies(self, plugin_name: str) -> Dict[str, bool]:
        """Check if plugin dependencies are satisfied"""
        if plugin_name not in self.plugins:
            return {"valid": False, "missing": [], "reason": "Plugin not found"}

        plugin = self.plugins[plugin_name]
        missing = [dep for dep in plugin.dependencies if dep not in self.algorithms]

        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "satisfied": [dep for dep in plugin.dependencies if dep in self.algorithms]
        }

    def analyze_passage(self, passage: BiblicalPassage, algorithm_name: str) -> Optional[AlgorithmicResult]:
        """Apply an algorithm to a passage with dependency checking"""
        if algorithm_name not in self.algorithms:
            return None

        # Check dependencies
        dep_check = self.check_dependencies(algorithm_name)
        if not dep_check["valid"]:
            return None  # Could return error result instead

        algorithm = self.algorithms[algorithm_name]
        result = algorithm(passage)

        return AlgorithmicResult(
            algorithm_name=algorithm_name,
            input_passage=passage,
            findings=result.get('findings', {}),
            insights=result.get('insights', []),
            confidence=result.get('confidence', 1.0)
        )

    def cache_passage(self, passage: BiblicalPassage):
        """Cache a passage for reuse"""
        key = f"{passage.reference}_{passage.version}"
        self.passage_cache[key] = passage

    def get_cached_passage(self, reference: str, version: str = "ESV") -> Optional[BiblicalPassage]:
        """Retrieve a cached passage"""
        key = f"{reference}_{version}"
        return self.passage_cache.get(key)

    def chain_algorithms(self, passage: BiblicalPassage, algorithm_names: List[str]) -> List[AlgorithmicResult]:
        """Apply multiple algorithms in sequence to a passage"""
        results = []
        for name in algorithm_names:
            result = self.analyze_passage(passage, name)
            if result:
                results.append(result)
        return results

    def analyze_by_category(self, passage: BiblicalPassage, category: str) -> List[AlgorithmicResult]:
        """Apply all algorithms in a category to a passage"""
        algorithm_names = self.categories.get(category, [])
        return self.chain_algorithms(passage, algorithm_names)

    def get_algorithms_by_tag(self, tag: str) -> List[str]:
        """Get algorithm names that have a specific tag"""
        return [name for name, plugin in self.plugins.items() if tag in plugin.tags]

    def multiply_analysis(self, passage: BiblicalPassage) -> Dict[str, List[AlgorithmicResult]]:
        """Generate 3-fold multiplied analysis (basic, advanced, interpretive)"""
        all_algos = list(self.algorithms.keys())

        # Basic: apply first algorithm
        basic = self.chain_algorithms(passage, all_algos[:1]) if all_algos else []

        # Advanced: apply all algorithms
        advanced = self.chain_algorithms(passage, all_algos)

        # Interpretive: apply algorithms with variations (e.g., reverse order)
        interpretive = self.chain_algorithms(passage, list(reversed(all_algos)))

        return {
            "basic": basic,
            "advanced": advanced,
            "interpretive": interpretive
        }

    def load_plugin_from_module(self, module_name: str, plugin_class_name: str = None):
        """Dynamically load a plugin from a Python module"""
        try:
            import importlib
            module = importlib.import_module(module_name)
            if plugin_class_name:
                plugin_class = getattr(module, plugin_class_name)
                plugin_instance = plugin_class()
                # Assume plugin has register method
                plugin_instance.register(self)
            else:
                # Assume module has register function
                module.register_plugin(self)
        except ImportError:
            print(f"Could not load plugin module: {module_name}")
        except AttributeError:
            print(f"Plugin class or function not found in module: {module_name}")

    def export_results(self, results: List[AlgorithmicResult], filename: str):
        """Export results to JSON"""
        data = {
            "version": __version__,
            "export_date": datetime.now().isoformat(),
            "results": [
                {
                    "algorithm": r.algorithm_name,
                    "passage": {
                        "reference": r.input_passage.reference,
                        "text": r.input_passage.text,
                        "version": r.input_passage.version
                    },
                    "findings": r.findings,
                    "insights": r.insights,
                    "confidence": r.confidence,
                    "timestamp": r.timestamp
                }
                for r in results
            ]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def analyze_passage_against_corpus(self, passage: BiblicalPassage, corpus: List[BiblicalPassage], algorithm_name: str) -> List[AlgorithmicResult]:
        """Analyze passage against a corpus using specified algorithm"""
        results = []
        for corpus_passage in corpus:
            if corpus_passage.reference != passage.reference:  # Don't analyze against itself
                result = self.analyze_passage(corpus_passage, algorithm_name)
                if result:
                    # Add link back to the original passage
                    result.links.append(LinkedPassage(
                        reference=passage.reference,
                        relationship="corpus_comparison",
                        insight=f"Compared against {corpus_passage.reference} using {algorithm_name}"
                    ))
                    results.append(result)
        return results

    def analyze_corpus(self, passages: List[BiblicalPassage], algorithm_names: List[str] = None) -> List[MultiDimensionalResult]:
        """Analyze multiple passages using all available algorithms"""
        if algorithm_names is None:
            algorithm_names = list(self.algorithms.keys())

        results = []
        analyzer = MultiDimensionalAnalyzer(self.framework if hasattr(self, 'framework') else self)

        for i, passage in enumerate(passages):
            print(f"Analyzing passage {i+1}/{len(passages)}: {passage.reference}")
            try:
                result = analyzer.analyze(passage)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {passage.reference}: {e}")
                continue

        return results

    def export_multidimensional_markdown(self, results: List[MultiDimensionalResult], filename: str):
        """Export multi-dimensional results to Markdown"""
        with open(filename, 'w') as f:
            f.write(f"# Bible Algorithmic Project - Multi-Dimensional Analysis Report\n\n")
            f.write(f"**Version:** {__version__}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for i, result in enumerate(results, 1):
                f.write(f"## Analysis {i}: {result.passage.reference}\n\n")
                f.write(f"**Text:** {result.passage.text}\n\n")
                f.write(f"**Version:** {result.passage.version}\n\n")
                f.write(f"**Metadata:**\n")
                f.write(f"- Word Count: {result.passage.word_count}\n")
                f.write(f"- Keywords: {', '.join(result.passage.keywords)}\n")
                f.write(f"- Themes: {', '.join(result.passage.themes)}\n\n")

                f.write(f"**Summary:** {result.synthesis}\n\n")
                f.write(f"**Metrics:**\n")
                f.write(f"- Dimensions Analyzed: {len(result.dimension_results)}\n")
                f.write(f"- Total Insights: {result.get_total_insights()}\n")
                f.write(f"- Total Findings: {result.get_total_findings()}\n")
                f.write(f"- Average Confidence: {result.get_average_confidence():.2f}\n")
                f.write(f"- Multiplication Factor: {result.multiplication_factor}x\n\n")

                for dim, dim_result in result.dimension_results.items():
                    f.write(f"### {dim.value.title()} Analysis\n\n")
                    f.write(f"**Confidence:** {dim_result.confidence}\n\n")
                    f.write(f"**Findings:**\n")
                    for key, value in dim_result.findings.items():
                        f.write(f"- {key}: {value}\n")
                    f.write(f"\n**Insights:**\n")
                    for insight in dim_result.insights:
                        f.write(f"- {insight}\n")
                    if dim_result.links:
                        f.write(f"\n**Connections:**\n")
                        for link in dim_result.links:
                            f.write(f"- {link.reference} ({link.relationship}): {link.insight}\n")
                    f.write(f"\n")

                f.write("---\n\n")

    def export_multidimensional_results(self, results: List[MultiDimensionalResult], filename: str):
        """Export multi-dimensional results to JSON"""
        data = {
            "version": __version__,
            "export_date": datetime.now().isoformat(),
            "results": [
                {
                    "passage": {
                        "reference": r.passage.reference,
                        "text": r.passage.text,
                        "version": r.passage.version,
                        "metadata": {
                            "word_count": r.passage.word_count,
                            "keywords": r.passage.keywords,
                            "themes": r.passage.themes
                        }
                    },
                    "dimensions_analyzed": len(r.dimension_results),
                    "total_insights": r.get_total_insights(),
                    "total_findings": r.get_total_findings(),
                    "average_confidence": r.get_average_confidence(),
                    "multiplication_factor": r.multiplication_factor,
                    "synthesis": r.synthesis,
                    "dimension_results": {
                        dim.value: {
                            "findings": result.findings,
                            "insights": result.insights,
                            "confidence": result.confidence,
                            "links": [{"reference": link.reference, "relationship": link.relationship, "insight": link.insight} for link in result.links]
                        }
                        for dim, result in r.dimension_results.items()
                    },
                    "timestamp": r.timestamp
                }
                for r in results
            ]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def export_interactive_html(self, results: List[MultiDimensionalResult], filename: str,
                               include_visualizations: bool = True):
        """Export multi-dimensional results to interactive HTML with modern UI"""
        html_content = self._generate_html_header()
        html_content += self._generate_html_body(results, include_visualizations)
        html_content += self._generate_html_footer()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_html_header(self) -> str:
        """Generate HTML header with CSS and JavaScript"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bible Algorithmic Project - Interactive Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }

        .header p {
            color: #7f8c8d;
            font-size: 1.1em;
        }

        .summary-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .metric {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }

        .metric h3 {
            font-size: 2em;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .metric p {
            color: #7f8c8d;
            font-size: 0.9em;
        }

        .passage-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .passage-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }

        .passage-header:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }

        .passage-title {
            font-size: 1.3em;
            font-weight: 500;
        }

        .passage-meta {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .toggle-icon {
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }

        .passage-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.5s ease;
        }

        .passage-content.expanded {
            max-height: 2000px;
        }

        .passage-text {
            padding: 25px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 1.1em;
            line-height: 1.7;
            color: #2c3e50;
        }

        .analysis-section {
            padding: 25px;
        }

        .dimension-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .dimension-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #3498db;
        }

        .dimension-card h4 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.1em;
        }

        .confidence-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }

        .confidence-high { background: #d4edda; color: #155724; }
        .confidence-medium { background: #fff3cd; color: #856404; }
        .confidence-low { background: #f8d7da; color: #721c24; }

        .insights-list {
            margin-top: 15px;
        }

        .insight-item {
            background: white;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 6px;
            border-left: 3px solid #3498db;
            font-size: 0.9em;
        }

        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .chart-title {
            font-size: 1.2em;
            color: #2c3e50;
            margin-bottom: 15px;
            text-align: center;
        }

        .footer {
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }

            .header h1 {
                font-size: 2em;
            }

            .dimension-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
"""

    def _generate_html_body(self, results: List[MultiDimensionalResult], include_visualizations: bool) -> str:
        """Generate HTML body content"""
        body = '<div class="container">\n'

        # Header
        body += f'''
    <div class="header">
        <h1>📖 Bible Algorithmic Project</h1>
        <p>Interactive Multi-Dimensional Analysis Report | Version {__version__}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
'''

        # Summary statistics
        total_passages = len(results)
        total_insights = sum(r.get_total_insights() for r in results)
        total_findings = sum(r.get_total_findings() for r in results)
        avg_confidence = sum(r.get_average_confidence() for r in results) / total_passages if results else 0

        body += f'''
    <div class="summary-card">
        <h2>📊 Analysis Summary</h2>
        <div class="summary-grid">
            <div class="metric">
                <h3>{total_passages}</h3>
                <p>Passages Analyzed</p>
            </div>
            <div class="metric">
                <h3>{total_insights}</h3>
                <p>Total Insights</p>
            </div>
            <div class="metric">
                <h3>{total_findings}</h3>
                <p>Total Findings</p>
            </div>
            <div class="metric">
                <h3>{avg_confidence:.2f}</h3>
                <p>Average Confidence</p>
            </div>
        </div>
    </div>
'''

        # Overall visualizations
        if include_visualizations and results:
            body += self._generate_overall_charts(results)

        # Individual passage analyses
        for i, result in enumerate(results, 1):
            body += self._generate_passage_html(result, i)

        body += '</div>\n'
        return body

    def _generate_overall_charts(self, results: List[MultiDimensionalResult]) -> str:
        """Generate overall analysis charts"""
        # Prepare data for charts
        dimension_counts = {}
        confidence_scores = []

        for result in results:
            confidence_scores.append(result.get_average_confidence())
            for dim in result.dimension_results.keys():
                dim_name = dim.value
                dimension_counts[dim_name] = dimension_counts.get(dim_name, 0) + 1

        charts_html = '''
    <div class="summary-card">
        <h2>📈 Overall Analysis Visualizations</h2>
        <div class="chart-container">
            <div class="chart-title">Dimensions Analyzed Across All Passages</div>
            <canvas id="dimensionsChart" width="400" height="200"></canvas>
        </div>
        <div class="chart-container">
            <div class="chart-title">Confidence Score Distribution</div>
            <canvas id="confidenceChart" width="400" height="200"></canvas>
        </div>
    </div>

    <script>
        // Dimensions chart
        const dimensionsCtx = document.getElementById('dimensionsChart').getContext('2d');
        new Chart(dimensionsCtx, {
            type: 'bar',
            data: {
                labels: ''' + str(list(dimension_counts.keys())) + ''',
                datasets: [{
                    label: 'Passages',
                    data: ''' + str(list(dimension_counts.values())) + ''',
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Confidence chart
        const confidenceCtx = document.getElementById('confidenceChart').getContext('2d');
        const confidenceData = ''' + str(confidence_scores) + ''';
        const confidenceBuckets = [0, 0, 0]; // low, medium, high

        confidenceData.forEach(score => {
            if (score >= 0.8) confidenceBuckets[2]++;
            else if (score >= 0.6) confidenceBuckets[1]++;
            else confidenceBuckets[0]++;
        });

        new Chart(confidenceCtx, {
            type: 'pie',
            data: {
                labels: ['Low (< 0.6)', 'Medium (0.6-0.8)', 'High (> 0.8)'],
                datasets: [{
                    data: confidenceBuckets,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });
    </script>
'''

        return charts_html

    def _generate_passage_html(self, result: MultiDimensionalResult, index: int) -> str:
        """Generate HTML for individual passage analysis"""
        confidence_class = "confidence-high" if result.get_average_confidence() >= 0.8 else \
                          "confidence-medium" if result.get_average_confidence() >= 0.6 else "confidence-low"

        passage_html = f'''
    <div class="passage-card">
        <div class="passage-header" onclick="togglePassage({index})">
            <div>
                <div class="passage-title">{result.passage.reference}</div>
                <div class="passage-meta">
                    {result.passage.version} | {result.passage.book} {result.passage.chapter}:{result.passage.verse} |
                    {len(result.dimension_results)} dimensions |
                    <span class="confidence-badge {confidence_class}">{result.get_average_confidence():.2f}</span>
                </div>
            </div>
            <div class="toggle-icon" id="icon-{index}">▼</div>
        </div>
        <div class="passage-content" id="content-{index}">
            <div class="passage-text">
                <strong>Text:</strong> {result.passage.text}
            </div>
            <div class="analysis-section">
                <h3>🔍 Multi-Dimensional Analysis</h3>
                <p><strong>Synthesis:</strong> {result.synthesis}</p>
                <p><strong>Multiplication Factor:</strong> {result.multiplication_factor}x</p>

                <div class="dimension-grid">
'''

        # Add each dimension
        for dim, dim_result in result.dimension_results.items():
            confidence_class = "confidence-high" if dim_result.confidence >= 0.8 else \
                              "confidence-medium" if dim_result.confidence >= 0.6 else "confidence-low"

            passage_html += f'''
                    <div class="dimension-card">
                        <h4>{dim.value.title()} Analysis</h4>
                        <div class="confidence-badge {confidence_class}">{dim_result.confidence:.2f}</div>
                        <div class="insights-list">
'''

            for insight in dim_result.insights[:3]:  # Show top 3 insights
                passage_html += f'<div class="insight-item">{insight}</div>'

            passage_html += '''
                        </div>
                    </div>
'''

        passage_html += '''
                </div>
            </div>
        </div>
    </div>
'''

        return passage_html

    def _generate_html_footer(self) -> str:
        """Generate HTML footer with JavaScript"""
        return '''
    <div class="footer">
        <p>Generated by Bible Algorithmic Project v''' + str(__version__) + ''' | ''' + datetime.now().strftime('%Y-%m-%d') + '''</p>
    </div>

    <script>
        function togglePassage(index) {
            const content = document.getElementById(`content-${index}`);
            const icon = document.getElementById(`icon-${index}`);

            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                icon.textContent = '▼';
            } else {
                content.classList.add('expanded');
                icon.textContent = '▲';
            }
        }

        // Expand first passage by default
        document.addEventListener('DOMContentLoaded', function() {
            togglePassage(1);
        });
    </script>
</body>
</html>'''

class MultiDimensionalAnalyzer:
    """Orchestrates multi-dimensional biblical analysis with plugin integration"""

    def __init__(self, framework: AlgorithmicFramework):
        self.framework = framework
        self.dimension_algorithms = {
            AnalysisDimension.LEXICAL: "lexical_analysis",
            AnalysisDimension.THEMATIC: "thematic_extraction",
            AnalysisDimension.STRUCTURAL: "structural_analysis",
            AnalysisDimension.CHRISTOLOGICAL: "christological_analysis",
            AnalysisDimension.CROSS_REFERENCE: "cross_reference_detection",
            AnalysisDimension.LITERARY: "literary_analysis",
            AnalysisDimension.ETHICAL: "ethical_analysis",
            AnalysisDimension.TEMPORAL: "temporal_analysis",
            AnalysisDimension.ESCHATOLOGICAL: "eschatological_analysis",
            AnalysisDimension.HISTORICAL: "historical_analysis"
        }
        self.dimension_categories = {
            AnalysisDimension.LEXICAL: "lexical",
            AnalysisDimension.THEMATIC: "thematic",
            AnalysisDimension.STRUCTURAL: "structural",
            AnalysisDimension.CHRISTOLOGICAL: "christological",
            AnalysisDimension.CROSS_REFERENCE: "cross_reference",
            AnalysisDimension.LITERARY: "literary",
            AnalysisDimension.ETHICAL: "ethical",
            AnalysisDimension.TEMPORAL: "temporal",
            AnalysisDimension.ESCHATOLOGICAL: "eschatological",
            AnalysisDimension.HISTORICAL: "historical"
        }

    def analyze(self, passage: BiblicalPassage) -> MultiDimensionalResult:
        """Perform multi-dimensional analysis"""
        dimension_results = {}

        for dimension, algo_name in self.dimension_algorithms.items():
            if algo_name in self.framework.algorithms:
                result = self.framework.analyze_passage(passage, algo_name)
                if result:
                    dimension_results[dimension] = DimensionalAnalysis(
                        dimension=dimension,
                        findings=result.findings,
                        insights=result.insights,
                        confidence=result.confidence,
                        links=result.links
                    )

        # Generate synthesis
        synthesis = self._generate_synthesis(passage, dimension_results)

        return MultiDimensionalResult(
            passage=passage,
            dimension_results=dimension_results,
            synthesis=synthesis,
            multiplication_factor=len(dimension_results)
        )

    def _generate_synthesis(self, passage: BiblicalPassage, dimension_results: Dict[AnalysisDimension, DimensionalAnalysis]) -> str:
        """Generate human-readable synthesis"""
        total_insights = sum(len(result.insights) for result in dimension_results.values())
        total_findings = sum(len(result.findings) for result in dimension_results.values())
        avg_confidence = sum(result.confidence for result in dimension_results.values()) / len(dimension_results) if dimension_results else 0.0

        dimensions_analyzed = [d.value for d in dimension_results.keys()]

        synthesis = f"Multi-dimensional analysis of {passage.reference} across {len(dimension_results)} dimensions revealed {total_insights} insights from {total_findings} distinct findings. "
        synthesis += f"Dimensions analyzed: {', '.join(dimensions_analyzed)}. "
        synthesis += f"Average confidence: {avg_confidence:.2f}."

        return synthesis

class LayeredGrowthEngine:
    """Implements recursive interpretive enrichment (ChatGPT-5 vision)"""

    def __init__(self, framework: AlgorithmicFramework):
        self.framework = framework

    def grow(self, passage: BiblicalPassage, layers: int = 5) -> List[AlgorithmicResult]:
        """Grow interpretive layers recursively"""
        layer_results = []
        current_passage = passage

        for i in range(layers):
            layer_insights = []

            for algo_name in self.framework.algorithms.keys():
                result = self.framework.analyze_passage(current_passage, algo_name)
                if result:
                    # Add layer metadata to passage for next iteration
                    current_passage.metadata[f"layer_{i+1}_{algo_name}"] = result.findings
                    layer_results.append(result)
                    layer_insights.extend(result.insights)

            # Update passage with accumulated insights
            current_passage.metadata[f"layer_{i+1}_insights"] = layer_insights

        return layer_results

class DimensionInteractionAnalyzer:
    """Analyzes interactions and resonances between dimensions"""

    def analyze_interactions(self, dimension_results: Dict[AnalysisDimension, DimensionalAnalysis]) -> Dict[str, Any]:
        """Detect meaningful patterns across dimensions"""
        interactions = {
            "reinforcements": self._find_reinforcements(dimension_results),
            "tensions": self._find_tensions(dimension_results),
            "resonance_score": self._calculate_resonance(dimension_results),
            "emergent_patterns": self._detect_emergence(dimension_results),
            "semantic_interactions": self.analyze_semantic_level(dimension_results),
            "theological_synthesis": self.analyze_theological_level(dimension_results)
        }
        return interactions

    def _find_reinforcements(self, results: Dict[AnalysisDimension, DimensionalAnalysis]) -> List[Dict]:
        """Find where dimensions reinforce each other"""
        reinforcements = []

        # Lexical repetition reinforces literary patterns
        if AnalysisDimension.LEXICAL in results and AnalysisDimension.LITERARY in results:
            lexical = results[AnalysisDimension.LEXICAL]
            literary = results[AnalysisDimension.LITERARY]

            lexical_repetitions = lexical.findings.get("most_frequent_words", [])
            literary_repetitions = literary.findings.get("repetition_patterns", {})

            if lexical_repetitions and literary_repetitions:
                reinforcements.append({
                    "type": "lexical_literary_reinforcement",
                    "description": "High lexical repetition patterns reinforce literary structure",
                    "strength": min(len(lexical_repetitions), len(literary_repetitions)) / 5.0
                })

        # Thematic density reinforces ethical content
        if AnalysisDimension.THEMATIC in results and AnalysisDimension.ETHICAL in results:
            thematic = results[AnalysisDimension.THEMATIC]
            ethical = results[AnalysisDimension.ETHICAL]

            theme_density = thematic.findings.get("theme_density", 0)
            moral_density = ethical.findings.get("moral_density", 0)

            if theme_density > 0.05 and moral_density > 0.02:
                reinforcements.append({
                    "type": "thematic_ethical_reinforcement",
                    "description": "Strong thematic content reinforces ethical teachings",
                    "strength": min(theme_density, moral_density) * 10
                })

        return reinforcements

    def _find_tensions(self, results: Dict[AnalysisDimension, DimensionalAnalysis]) -> List[Dict]:
        """Find where dimensions show tension or contrast"""
        tensions = []

        # Simple structure vs complex themes
        if AnalysisDimension.STRUCTURAL in results and AnalysisDimension.THEMATIC in results:
            structural = results[AnalysisDimension.STRUCTURAL]
            thematic = results[AnalysisDimension.THEMATIC]

            sentence_count = structural.findings.get("sentence_count", 1)
            theme_count = thematic.findings.get("theme_count", 0)

            if sentence_count == 1 and theme_count > 2:
                tensions.append({
                    "type": "structural_thematic_tension",
                    "description": "Simple sentence structure contrasts with complex thematic content",
                    "strength": theme_count / sentence_count
                })

        return tensions

    def _calculate_resonance(self, results: Dict[AnalysisDimension, DimensionalAnalysis]) -> float:
        """Calculate overall resonance score across dimensions"""
        if not results:
            return 0.0

        # Average confidence weighted by interaction potential
        total_weighted_confidence = 0.0
        total_weight = 0.0

        dimension_weights = {
            AnalysisDimension.LEXICAL: 1.0,
            AnalysisDimension.THEMATIC: 1.2,
            AnalysisDimension.STRUCTURAL: 0.8,
            AnalysisDimension.CHRISTOLOGICAL: 1.5,
            AnalysisDimension.CROSS_REFERENCE: 1.3,
            AnalysisDimension.LITERARY: 1.1,
            AnalysisDimension.ETHICAL: 1.4,
            AnalysisDimension.TEMPORAL: 1.0,
            AnalysisDimension.ESCHATOLOGICAL: 1.3,
            AnalysisDimension.HISTORICAL: 1.1
        }

        for dimension, result in results.items():
            weight = dimension_weights.get(dimension, 1.0)
            total_weighted_confidence += result.confidence * weight
            total_weight += weight

        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0

    def _detect_emergence(self, results: Dict[AnalysisDimension, DimensionalAnalysis]) -> List[Dict]:
        """Detect emergent patterns that arise from dimension interactions"""
        emergent = []

        # Check for "creation narrative" pattern
        creation_indicators = 0
        if AnalysisDimension.THEMATIC in results:
            themes = results[AnalysisDimension.THEMATIC].findings.get("detected_themes", {})
            if "creation" in themes:
                creation_indicators += 1

        if AnalysisDimension.TEMPORAL in results:
            dominant_tense = results[AnalysisDimension.TEMPORAL].findings.get("dominant_tense", "")
            if dominant_tense == "past":
                creation_indicators += 1

        if AnalysisDimension.HISTORICAL in results:
            context_type = results[AnalysisDimension.HISTORICAL].findings.get("context_type", "")
            if context_type in ["strongly_historical", "historically_rooted"]:
                creation_indicators += 1

        if creation_indicators >= 2:
            emergent.append({
                "pattern": "creation_narrative",
                "description": "Multiple dimensions suggest a creation/origins narrative",
                "supporting_dimensions": creation_indicators,
                "confidence": min(creation_indicators / 3.0, 1.0)
            })

        return emergent

    def analyze_semantic_level(self, results: Dict[AnalysisDimension, DimensionalAnalysis]) -> List[Dict]:
        """Detect meaning-level interactions"""
        semantic_patterns = []

        # Example: Repetition (lexical) of "Word" + high christological context
        if AnalysisDimension.LEXICAL in results and AnalysisDimension.CHRISTOLOGICAL in results:
            lexical = results[AnalysisDimension.LEXICAL]
            christological = results[AnalysisDimension.CHRISTOLOGICAL]

            # Check for capitalized significant terms
            word_freq = dict(lexical.findings.get("most_frequent_words", []))

            # Check passage for capitalized "Word" - likely a title
            if "word" in word_freq and word_freq["word"] > 1:
                contextual_titles = christological.findings.get("contextual_christ_titles", [])
                if contextual_titles:
                    semantic_patterns.append({
                        "pattern": "potential_christological_title",
                        "description": "High-frequency term 'Word' may be christological title based on context",
                        "evidence": f"'Word' appears {word_freq['word']} times with contextual indicators",
                        "confidence": 0.85,
                        "supporting_dimensions": ["lexical", "christological"]
                    })

        # Cross-reference validation through thematic consistency
        if AnalysisDimension.CROSS_REFERENCE in results and AnalysisDimension.THEMATIC in results:
            cross_refs = results[AnalysisDimension.CROSS_REFERENCE].findings.get("cross_references", [])
            themes = results[AnalysisDimension.THEMATIC].findings.get("detected_themes", {})

            if cross_refs and themes:
                thematic_consistency = 0
                for ref in cross_refs:
                    ref_themes = self._get_reference_themes(ref["reference"])
                    shared_themes = set(ref_themes) & set(themes.keys())
                    if shared_themes:
                        thematic_consistency += len(shared_themes)

                if thematic_consistency > 0:
                    semantic_patterns.append({
                        "pattern": "thematic_cross_reference_validation",
                        "description": f"Cross-references validated by {thematic_consistency} shared theological themes",
                        "evidence": f"References and themes show {thematic_consistency} points of consistency",
                        "confidence": min(thematic_consistency / 5.0, 1.0),
                        "supporting_dimensions": ["cross_reference", "thematic"]
                    })

        return semantic_patterns

    def analyze_theological_level(self, results: Dict[AnalysisDimension, DimensionalAnalysis]) -> Dict[str, Any]:
        """Detect high-level theological patterns"""
        trinity_score = 0.0
        incarnation_score = 0.0
        creation_theology_score = 0.0

        # Trinity indicators (Father + Son + Spirit)
        if AnalysisDimension.THEMATIC in results:
            themes = results[AnalysisDimension.THEMATIC].findings.get("detected_themes", {})
            if "creation" in themes:
                creation_theology_score += 0.3

        if AnalysisDimension.TEMPORAL in results:
            dominant_tense = results[AnalysisDimension.TEMPORAL].findings.get("dominant_tense", "")
            thematic_result = results.get(AnalysisDimension.THEMATIC)
            if thematic_result and dominant_tense == "past" and "creation" in thematic_result.findings.get("detected_themes", {}):
                creation_theology_score += 0.3

        if AnalysisDimension.CHRISTOLOGICAL in results:
            christ_density = results[AnalysisDimension.CHRISTOLOGICAL].findings.get("christological_density", 0)
            if christ_density > 0:
                incarnation_score += christ_density * 2

        # Additional trinity detection
        if AnalysisDimension.CHRISTOLOGICAL in results and AnalysisDimension.THEMATIC in results:
            christ_titles = results[AnalysisDimension.CHRISTOLOGICAL].findings.get("christ_titles", [])
            themes = results[AnalysisDimension.THEMATIC].findings.get("detected_themes", {})

            # Look for relational language
            if any(title in ["son", "father", "spirit"] for title in christ_titles):
                trinity_score += 0.4
            if "kingdom" in themes:
                trinity_score += 0.3

        return {
            "trinity_theology_score": round(trinity_score, 2),
            "incarnation_theology_score": round(incarnation_score, 2),
            "creation_theology_score": round(creation_theology_score, 2),
            "dominant_theological_framework": self._identify_dominant_framework(
                trinity_score, incarnation_score, creation_theology_score
            )
        }

    def _get_reference_themes(self, reference: str) -> List[str]:
        """Get expected themes for a reference (simplified)"""
        theme_map = {
            "Genesis 1:1": ["creation"],
            "Proverbs 8:22": ["wisdom", "creation"],
            "Colossians 1:15": ["creation", "christ"],
            "Hebrews 11:3": ["creation", "faith"]
        }
        return theme_map.get(reference, [])

    def _identify_dominant_framework(self, trinity: float, incarnation: float, creation: float) -> str:
        scores = {"Trinitarian": trinity, "Incarnational": incarnation, "Creation": creation}
        if max(scores.values()) < 0.2:
            return "Undetermined"
        return max(scores, key=scores.get)

class SowerMetrics:
    """Quantifies interpretive multiplication progress (Matthew 13:8)"""

    def compute_metrics(self, results: List[MultiDimensionalResult]) -> Dict[str, float]:
        """Calculate interpretive yield metrics"""
        if not results:
            return {"interpretive_yield": 0.0, "average_fold": 0.0, "growth_index": 0.0}

        total_insights = sum(r.get_total_insights() for r in results)
        avg_fold = sum(r.multiplication_factor for r in results) / len(results)

        # Growth index: insights × fold factor / baseline (10 = symbolic "tenfold")
        growth_index = round(total_insights * avg_fold / 10, 2)

        return {
            "interpretive_yield": round(total_insights / len(results), 2),
            "average_fold": round(avg_fold, 1),
            "growth_index": growth_index
        }

    def get_sower_classification(self, growth_index: float) -> str:
        """Classify growth according to Parable of the Sower"""
        if growth_index >= 30:
            return "thirtyfold_fruit"
        elif growth_index >= 20:
            return "twentyfold_fruit"
        elif growth_index >= 10:
            return "tenfold_fruit"
        elif growth_index >= 6:
            return "sixfold_fruit"
        else:
            return "minimal_fruit"

@dataclass
class GenreClassification:
    """Result of genre classification"""
    primary_genre: str
    secondary_genres: List[str]
    confidence_scores: Dict[str, float]
    detection_features: Dict[str, Any]
    genre_characteristics: Dict[str, Any]

class GenreDetector:
    """Detects biblical literary genres using linguistic and thematic features"""

    def __init__(self):
        self.genres = {
            "narrative": {
                "description": "Story-like passages with chronological sequence",
                "key_features": ["past_tense", "sequence_words", "character_actions", "plot_elements"],
                "indicators": {
                    "tense_markers": ["was", "were", "had", "did", "came", "went", "said", "told"],
                    "sequence_words": ["then", "after", "before", "when", "next", "afterward"],
                    "narrative_verbs": ["went", "came", "said", "saw", "heard", "told", "asked"],
                    "character_indicators": ["he", "she", "they", "man", "woman", "people", "crowd"]
                }
            },
            "poetry": {
                "description": "Poetic passages with parallelism and imagery",
                "key_features": ["parallelism", "imagery", "rhythm", "metaphor"],
                "indicators": {
                    "parallel_structures": ["and", "but", "yet", "or", "nor", "for", "so"],
                    "imagery_words": ["like", "as", "heart", "soul", "spirit", "voice", "cry"],
                    "poetic_devices": ["metaphor", "simile", "personification", "symbol"],
                    "rhythm_indicators": ["repetition", "pattern", "structure", "form"]
                }
            },
            "prophecy": {
                "description": "Prophetic utterances with future orientation",
                "key_features": ["future_tense", "judgment_themes", "divine_speech", "warning"],
                "indicators": {
                    "future_markers": ["will", "shall", "come", "arise", "establish", "destroy"],
                    "prophetic_formulas": ["thus says", "hear the word", "oracle", "vision"],
                    "judgment_words": ["judgment", "wrath", "punishment", "destruction", "repent"],
                    "divine_speech": ["says the lord", "declares the lord", "word of the lord"]
                }
            },
            "wisdom": {
                "description": "Wisdom literature with proverbs and instruction",
                "key_features": ["instruction", "proverbs", "moral_teaching", "practical_advice"],
                "indicators": {
                    "wisdom_terms": ["wise", "wisdom", "understanding", "knowledge", "instruction"],
                    "proverb_markers": ["whoever", "blessed is", "cursed is", "better to"],
                    "instruction_words": ["listen", "hear", "pay attention", "learn", "teach"],
                    "moral_terms": ["righteous", "wicked", "fool", "wise man", "foolish"]
                }
            },
            "gospel": {
                "description": "Gospel narratives about Jesus' life and teachings",
                "key_features": ["jesus_focus", "miracles", "teachings", "disciples"],
                "indicators": {
                    "jesus_titles": ["jesus", "christ", "son of man", "son of god", "master", "teacher"],
                    "gospel_events": ["miracle", "healing", "teaching", "parable", "crucifixion"],
                    "disciples": ["peter", "john", "james", "andrew", "philip", "bartholomew"],
                    "gospel_locations": ["galilee", "jerusalem", "jordan", "sea of galilee", "synagogue"]
                }
            },
            "epistle": {
                "description": "Letters with greetings, instruction, and exhortation",
                "key_features": ["epistolary_form", "greetings", "exhortation", "church_focus"],
                "indicators": {
                    "epistolary_markers": ["grace", "peace", "brethren", "saints", "beloved"],
                    "greetings": ["greetings", "grace to you", "mercy", "peace be with you"],
                    "exhortation": ["therefore", "so then", "now", "finally", "brothers"],
                    "church_terms": ["church", "assembly", "congregation", "fellowship", "ministry"]
                }
            },
            "apocalyptic": {
                "description": "Apocalyptic literature with symbolic visions",
                "key_features": ["symbolism", "visions", "cosmic_events", "end_times"],
                "indicators": {
                    "apocalyptic_symbols": ["beast", "dragon", "throne", "crown", "scroll", "seal"],
                    "vision_language": ["saw", "beheld", "vision", "dream", "revelation", "appeared"],
                    "cosmic_events": ["heaven", "earth", "stars", "angels", "thunder", "lightning"],
                    "end_times": ["end", "last", "final", "eternal", "judgment", "kingdom"]
                }
            },
            "historical": {
                "description": "Historical accounts and chronicles",
                "key_features": ["historical_figures", "chronology", "events", "genealogies"],
                "indicators": {
                    "historical_figures": ["king", "queen", "priest", "prophet", "judge", "ruler"],
                    "chronological_terms": ["year", "month", "day", "reign", "generation", "age"],
                    "historical_events": ["war", "battle", "conquest", "building", "temple", "palace"],
                    "genealogical_terms": ["son of", "father of", "begot", "descendants", "lineage"]
                }
            }
        }

    def classify_genre(self, passage: BiblicalPassage) -> GenreClassification:
        """Classify the genre of a biblical passage"""
        text_lower = passage.get_cached_text_lower()
        lemmas = passage.get_lemmas()
        lemma_text = ' '.join(lemmas)

        # Get analysis results for additional features
        lexical_result = lexical_analysis(passage)
        thematic_result = thematic_extraction(passage)
        structural_result = structural_analysis(passage)
        temporal_result = temporal_analysis(passage)

        confidence_scores = {}
        detection_features = {}

        for genre, genre_data in self.genres.items():
            score = 0.0
            features_found = {}

            # Analyze each indicator category
            for indicator_type, indicators in genre_data["indicators"].items():
                matches = 0
                for indicator in indicators:
                    # Check in original text and lemmas
                    if indicator in text_lower or indicator in lemma_text:
                        matches += 1

                # Weight matches by category importance
                if indicator_type == "tense_markers":
                    weight = 1.5 if genre in ["narrative", "historical"] else 1.0
                elif indicator_type == "future_markers":
                    weight = 1.5 if genre == "prophecy" else 1.0
                elif indicator_type == "jesus_titles":
                    weight = 2.0 if genre == "gospel" else 0.5
                else:
                    weight = 1.0

                score += (matches / len(indicators)) * weight
                features_found[indicator_type] = matches

            # Genre-specific analysis enhancements
            if genre == "narrative":
                # High past tense + sequence words
                past_tense_ratio = temporal_result["findings"]["tense_distribution"].get("past", 0) / sum(temporal_result["findings"]["tense_distribution"].values()) if temporal_result["findings"]["tense_distribution"] else 0
                repetition_count = sum(structural_result["findings"]["word_repetitions"].values()) if structural_result["findings"]["word_repetitions"] else 0
                sequence_ratio = repetition_count / len(passage.get_cached_words()) if passage.get_cached_words() else 0
                score += (past_tense_ratio + sequence_ratio) * 0.5

            elif genre == "poetry":
                # Parallelism and imagery
                literary_result = literary_analysis(passage)
                parallelism_score = len(literary_result["findings"]["repetition_patterns"]) / len(passage.get_cached_words()) if passage.get_cached_words() else 0
                imagery_score = len(literary_result["findings"]["imagery_detected"]) / 5.0  # Normalize to 5 senses
                score += (parallelism_score + imagery_score) * 0.8

            elif genre == "prophecy":
                # Future orientation + judgment themes
                future_tense_ratio = temporal_result["findings"]["tense_distribution"].get("future", 0) / sum(temporal_result["findings"]["tense_distribution"].values()) if temporal_result["findings"]["tense_distribution"] else 0
                eschatological_result = eschatological_analysis(passage)
                judgment_density = eschatological_result["findings"]["eschatological_density"]
                score += (future_tense_ratio + judgment_density) * 1.2

            elif genre == "wisdom":
                # Imperatives + moral teaching
                ethical_result = ethical_analysis(passage)
                imperative_density = ethical_result["findings"]["imperative_count"] / len(passage.get_cached_words()) if passage.get_cached_words() else 0
                virtue_density = len(ethical_result["findings"]["detected_virtues"]) / len(passage.get_cached_words()) if passage.get_cached_words() else 0
                score += (imperative_density + virtue_density) * 1.5

            elif genre == "gospel":
                # Jesus focus + narrative elements
                christological_result = christological_analysis(passage)
                jesus_density = christological_result["findings"]["christological_density"]
                narrative_score = confidence_scores.get("narrative", 0) * 0.3  # Partial narrative influence
                score += (jesus_density + narrative_score) * 1.8

            elif genre == "epistle":
                # Epistolary markers + exhortation
                epistle_markers = sum(1 for marker in ["grace", "peace", "brethren", "therefore"] if marker in text_lower)
                exhortation_density = epistle_markers / len(passage.get_cached_words()) if passage.get_cached_words() else 0
                score += exhortation_density * 2.0

            elif genre == "apocalyptic":
                # Symbolic language + visions
                apocalyptic_symbols = sum(1 for symbol in ["beast", "throne", "scroll", "heaven", "earth"] if symbol in text_lower)
                vision_density = apocalyptic_symbols / len(passage.get_cached_words()) if passage.get_cached_words() else 0
                score += vision_density * 2.5

            elif genre == "historical":
                # Historical figures + chronology
                historical_result = historical_analysis(passage)
                historical_density = historical_result["findings"]["historical_density"]
                chronological_score = temporal_result["findings"]["sequence_indicators"] / len(passage.get_cached_words()) if passage.get_cached_words() else 0
                score += (historical_density + chronological_score) * 1.3

            confidence_scores[genre] = min(score / 3.0, 1.0)  # Normalize to 0-1
            detection_features[genre] = features_found

        # Determine primary and secondary genres
        sorted_genres = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)
        primary_genre = sorted_genres[0][0]
        secondary_genres = [genre for genre, score in sorted_genres[1:3] if score > 0.3]  # Top 2 secondary if > 30%

        # Genre characteristics
        genre_characteristics = {
            "primary_features": self.genres[primary_genre]["key_features"],
            "confidence_distribution": confidence_scores,
            "genre_description": self.genres[primary_genre]["description"]
        }

        return GenreClassification(
            primary_genre=primary_genre,
            secondary_genres=secondary_genres,
            confidence_scores=confidence_scores,
            detection_features=detection_features,
            genre_characteristics=genre_characteristics
        )

@dataclass
class OntologyConcept:
    """A theological concept in the ontology"""
    name: str
    definition: str
    parent_concepts: List[str]
    child_concepts: List[str]
    related_concepts: List[str]
    key_terms: List[str]
    biblical_references: List[str]
    theological_weight: float = 1.0

@dataclass
class ConceptMapping:
    """Mapping of a passage to ontological concepts"""
    concept_name: str
    strength: float
    evidence_terms: List[str]
    contextual_relevance: float
    hierarchical_level: int

class TheologicalOntology:
    """Hierarchical theological concept ontology with relationship mapping"""

    def __init__(self):
        self.concepts = {}  # concept_name -> OntologyConcept
        self.concept_hierarchy = {}  # concept -> level in hierarchy
        self.build_ontology()

    def build_ontology(self):
        """Build the theological concept hierarchy"""

        # Level 1: Fundamental Categories
        fundamental_concepts = {
            "God": OntologyConcept(
                name="God",
                definition="The supreme being, eternal and transcendent",
                parent_concepts=[],
                child_concepts=["Creator", "Redeemer", "Sustainer", "Holy_Trinity"],
                related_concepts=["Divine_Nature", "Divine_Attributes"],
                key_terms=["god", "lord", "father", "almighty", "eternal"],
                biblical_references=["Exodus 3:14", "Deuteronomy 6:4", "Isaiah 44:6"],
                theological_weight=5.0
            ),
            "Humanity": OntologyConcept(
                name="Humanity",
                definition="Created beings made in God's image",
                parent_concepts=[],
                child_concepts=["Sinful_Nature", "Image_of_God", "Salvation"],
                related_concepts=["Creation", "Fall", "Redemption"],
                key_terms=["man", "woman", "human", "people", "mankind"],
                biblical_references=["Genesis 1:26-27", "Psalm 8:4-6"],
                theological_weight=4.0
            ),
            "Creation": OntologyConcept(
                name="Creation",
                definition="God's act of bringing the universe into existence",
                parent_concepts=[],
                child_concepts=["Cosmos", "Life", "Order"],
                related_concepts=["God", "Sovereignty", "Wisdom"],
                key_terms=["create", "made", "formed", "beginning", "heaven", "earth"],
                biblical_references=["Genesis 1:1", "Psalm 104", "Colossians 1:16"],
                theological_weight=4.5
            ),
            "Sin": OntologyConcept(
                name="Sin",
                definition="Rebellion against God's will and nature",
                parent_concepts=[],
                child_concepts=["Original_Sin", "Personal_Sin", "Consequences"],
                related_concepts=["Fall", "Judgment", "Redemption"],
                key_terms=["sin", "transgression", "iniquity", "wickedness", "evil"],
                biblical_references=["Genesis 3", "Romans 3:23", "1 John 1:8"],
                theological_weight=4.0
            ),
            "Salvation": OntologyConcept(
                name="Salvation",
                definition="Deliverance from sin through God's grace",
                parent_concepts=[],
                child_concepts=["Grace", "Faith", "Redemption", "Justification"],
                related_concepts=["Christ", "Cross", "Resurrection"],
                key_terms=["save", "salvation", "redeem", "deliver", "grace"],
                biblical_references=["John 3:16", "Romans 6:23", "Ephesians 2:8-9"],
                theological_weight=5.0
            )
        }

        # Level 2: Divine Attributes and Actions
        divine_concepts = {
            "Creator": OntologyConcept(
                name="Creator",
                definition="God as the maker of all things",
                parent_concepts=["God"],
                child_concepts=["Sovereign_Creator", "Wise_Creator"],
                related_concepts=["Creation", "Power", "Wisdom"],
                key_terms=["creator", "maker", "formed", "established"],
                biblical_references=["Genesis 1:1", "Isaiah 40:28", "Hebrews 11:3"],
                theological_weight=3.5
            ),
            "Redeemer": OntologyConcept(
                name="Redeemer",
                definition="God as the savior and deliverer",
                parent_concepts=["God"],
                child_concepts=["Savior", "Liberator"],
                related_concepts=["Salvation", "Christ", "Grace"],
                key_terms=["redeem", "save", "deliver", "ransom"],
                biblical_references=["Exodus 6:6", "Job 19:25", "Titus 2:14"],
                theological_weight=4.0
            ),
            "Holy_Trinity": OntologyConcept(
                name="Holy_Trinity",
                definition="God as Father, Son, and Holy Spirit",
                parent_concepts=["God"],
                child_concepts=["Father", "Son", "Holy_Spirit"],
                related_concepts=["Divine_Nature", "Relationship"],
                key_terms=["father", "son", "spirit", "trinity"],
                biblical_references=["Matthew 28:19", "2 Corinthians 13:14"],
                theological_weight=4.5
            )
        }

        # Level 2: Christological Concepts
        christ_concepts = {
            "Christ": OntologyConcept(
                name="Christ",
                definition="Jesus as the Messiah and Savior",
                parent_concepts=["Holy_Trinity"],
                child_concepts=["Messiah", "Son_of_God", "Son_of_Man"],
                related_concepts=["Incarnation", "Crucifixion", "Resurrection"],
                key_terms=["christ", "jesus", "messiah", "savior", "lord"],
                biblical_references=["Matthew 1:21", "John 1:41", "Acts 2:36"],
                theological_weight=5.0
            ),
            "Incarnation": OntologyConcept(
                name="Incarnation",
                definition="God becoming flesh in Jesus Christ",
                parent_concepts=["Christ"],
                child_concepts=["Word_Became_Flesh", "Fully_God_Fully_Man"],
                related_concepts=["Divine_Nature", "Human_Nature"],
                key_terms=["became flesh", "word became", "born of", "incarnate"],
                biblical_references=["John 1:14", "Philippians 2:6-8", "Colossians 2:9"],
                theological_weight=4.0
            )
        }

        # Level 2: Soteriological Concepts
        salvation_concepts = {
            "Grace": OntologyConcept(
                name="Grace",
                definition="Unmerited favor and blessing from God",
                parent_concepts=["Salvation"],
                child_concepts=["Saving_Grace", "Sustaining_Grace"],
                related_concepts=["Mercy", "Love", "Gift"],
                key_terms=["grace", "favor", "mercy", "gift", "unmerited"],
                biblical_references=["Ephesians 2:8-9", "Romans 3:24", "Titus 2:11"],
                theological_weight=3.5
            ),
            "Faith": OntologyConcept(
                name="Faith",
                definition="Trust and belief in God and His promises",
                parent_concepts=["Salvation"],
                child_concepts=["Saving_Faith", "Living_Faith"],
                related_concepts=["Trust", "Belief", "Assurance"],
                key_terms=["faith", "believe", "trust", "confidence"],
                biblical_references=["Hebrews 11:1", "Romans 1:17", "Ephesians 2:8"],
                theological_weight=3.5
            )
        }

        # Combine all concepts
        all_concepts = {}
        all_concepts.update(fundamental_concepts)
        all_concepts.update(divine_concepts)
        all_concepts.update(christ_concepts)
        all_concepts.update(salvation_concepts)

        # Set up hierarchy levels
        for concept in all_concepts.values():
            self.concepts[concept.name] = concept
            if not concept.parent_concepts:
                self.concept_hierarchy[concept.name] = 1
            else:
                # Find maximum parent level + 1
                parent_levels = [self.concept_hierarchy.get(parent, 1) for parent in concept.parent_concepts]
                self.concept_hierarchy[concept.name] = max(parent_levels) + 1

    def map_passage_to_concepts(self, passage: BiblicalPassage) -> List[ConceptMapping]:
        """Map a passage to theological concepts in the ontology"""
        text_lower = passage.get_cached_text_lower()
        lemmas = passage.get_lemmas()
        lemma_text = ' '.join(lemmas)

        mappings = []

        for concept_name, concept in self.concepts.items():
            strength = 0.0
            evidence_terms = []

            # Check key terms in text and lemmas
            for term in concept.key_terms:
                if term in text_lower or term in lemma_text:
                    evidence_terms.append(term)
                    # Weight by term frequency
                    term_count = text_lower.count(term) + lemma_text.count(term)
                    strength += term_count * concept.theological_weight

            # Normalize strength
            max_possible_strength = len(concept.key_terms) * concept.theological_weight * 3  # Assume max 3 occurrences
            if max_possible_strength > 0:
                strength = min(strength / max_possible_strength, 1.0)

            # Contextual relevance based on related concepts
            contextual_relevance = 0.0
            related_mappings = [m for m in mappings if m.concept_name in concept.related_concepts]
            if related_mappings:
                contextual_relevance = sum(m.strength for m in related_mappings) / len(related_mappings)

            # Boost strength if related concepts are present
            strength += contextual_relevance * 0.2
            strength = min(strength, 1.0)

            if strength > 0.1:  # Only include meaningful mappings
                hierarchical_level = self.concept_hierarchy.get(concept_name, 1)

                mappings.append(ConceptMapping(
                    concept_name=concept_name,
                    strength=strength,
                    evidence_terms=evidence_terms,
                    contextual_relevance=contextual_relevance,
                    hierarchical_level=hierarchical_level
                ))

        # Sort by strength
        mappings.sort(key=lambda x: x.strength, reverse=True)

        return mappings

    def get_concept_relationships(self, concept_name: str) -> Dict[str, List[str]]:
        """Get hierarchical and relational connections for a concept"""
        if concept_name not in self.concepts:
            return {}

        concept = self.concepts[concept_name]

        return {
            "parents": concept.parent_concepts,
            "children": concept.child_concepts,
            "related": concept.related_concepts,
            "level": self.concept_hierarchy.get(concept_name, 1)
        }

    def find_concept_path(self, from_concept: str, to_concept: str) -> List[str]:
        """Find the shortest path between two concepts in the ontology"""
        if from_concept not in self.concepts or to_concept not in self.concepts:
            return []

        # Simple BFS for path finding
        from collections import deque

        queue = deque([(from_concept, [from_concept])])
        visited = set()

        while queue:
            current, path = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if current == to_concept:
                return path

            # Add neighbors
            concept = self.concepts[current]
            neighbors = concept.parent_concepts + concept.child_concepts + concept.related_concepts

            for neighbor in neighbors:
                if neighbor not in visited and neighbor in self.concepts:
                    queue.append((neighbor, path + [neighbor]))

        return []  # No path found

    def get_theological_depth(self, mappings: List[ConceptMapping]) -> Dict[str, Any]:
        """Analyze the theological depth of concept mappings"""
        if not mappings:
            return {"depth_score": 0.0, "hierarchy_coverage": 0.0, "concept_diversity": 0.0}

        # Depth score based on hierarchical levels
        levels = [m.hierarchical_level for m in mappings]
        avg_level = sum(levels) / len(levels)
        depth_score = min(avg_level / 3.0, 1.0)  # Normalize to 3 levels max

        # Hierarchy coverage (how many levels represented)
        unique_levels = len(set(levels))
        hierarchy_coverage = unique_levels / 3.0  # Assuming 3 levels

        # Concept diversity (unique concepts vs total mappings)
        unique_concepts = len(set(m.concept_name for m in mappings))
        concept_diversity = unique_concepts / len(mappings)

        return {
            "depth_score": depth_score,
            "hierarchy_coverage": hierarchy_coverage,
            "concept_diversity": concept_diversity,
            "average_hierarchy_level": avg_level,
            "levels_represented": unique_levels
        }

@dataclass
class BatchAnalysisResult:
    """Result of batch analysis"""
    passages_analyzed: int
    total_insights: int
    average_confidence: float
    processing_time: float
    results: List[MultiDimensionalResult]
    batch_statistics: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class BatchAnalyzer:
    """Efficient batch processing for multiple passages with parallel capabilities"""

    def __init__(self, framework: AlgorithmicFramework, max_workers: int = 4):
        self.framework = framework
        self.max_workers = max_workers
        self.batch_cache = {}  # Cache for batch results

    def analyze_batch(self, passages: List[BiblicalPassage], algorithms: List[str] = None,
                     use_parallel: bool = True) -> BatchAnalysisResult:
        """Analyze multiple passages in batch with optional parallel processing"""
        import time
        start_time = time.time()

        if not passages:
            return BatchAnalysisResult(
                passages_analyzed=0,
                total_insights=0,
                average_confidence=0.0,
                processing_time=0.0,
                results=[],
                batch_statistics={}
            )

        # Check cache first
        cache_key = self._generate_cache_key(passages, algorithms)
        if cache_key in self.batch_cache:
            cached_result = self.batch_cache[cache_key]
            # Update timestamp but keep other data
            cached_result.timestamp = datetime.now().isoformat()
            return cached_result

        results = []

        if use_parallel and len(passages) > 1:
            results = self._analyze_parallel(passages, algorithms)
        else:
            results = self._analyze_sequential(passages, algorithms)

        processing_time = time.time() - start_time

        # Calculate batch statistics
        total_insights = sum(r.get_total_insights() for r in results)
        total_findings = sum(r.get_total_findings() for r in results)
        avg_confidence = sum(r.get_average_confidence() for r in results) / len(results) if results else 0.0

        batch_statistics = {
            "total_passages": len(passages),
            "total_insights": total_insights,
            "total_findings": total_findings,
            "average_insights_per_passage": total_insights / len(passages) if passages else 0,
            "average_findings_per_passage": total_findings / len(passages) if passages else 0,
            "average_confidence": avg_confidence,
            "processing_time_seconds": processing_time,
            "processing_rate": len(passages) / processing_time if processing_time > 0 else 0,
            "parallel_processing": use_parallel and len(passages) > 1,
            "algorithms_used": algorithms or list(self.framework.algorithms.keys())
        }

        batch_result = BatchAnalysisResult(
            passages_analyzed=len(passages),
            total_insights=total_insights,
            average_confidence=avg_confidence,
            processing_time=processing_time,
            results=results,
            batch_statistics=batch_statistics
        )

        # Cache the result
        self.batch_cache[cache_key] = batch_result

        return batch_result

    def _analyze_sequential(self, passages: List[BiblicalPassage], algorithms: List[str] = None) -> List[MultiDimensionalResult]:
        """Sequential analysis of passages"""
        results = []
        analyzer = MultiDimensionalAnalyzer(self.framework)

        for i, passage in enumerate(passages):
            print(f"Analyzing passage {i+1}/{len(passages)}: {passage.reference}")
            try:
                result = analyzer.analyze(passage)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {passage.reference}: {e}")
                continue

        return results

    def _analyze_parallel(self, passages: List[BiblicalPassage], algorithms: List[str] = None) -> List[MultiDimensionalResult]:
        """Parallel analysis using threading"""
        import concurrent.futures
        import threading

        results = []
        lock = threading.Lock()

        def analyze_single(passage):
            analyzer = MultiDimensionalAnalyzer(self.framework)
            try:
                result = analyzer.analyze(passage)
                with lock:
                    print(f"Completed analysis of {passage.reference}")
                return result
            except Exception as e:
                with lock:
                    print(f"Error analyzing {passage.reference}: {e}")
                return None

        # Use ThreadPoolExecutor for I/O bound tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_passage = {executor.submit(analyze_single, passage): passage for passage in passages}
            for future in concurrent.futures.as_completed(future_to_passage):
                result = future.result()
                if result:
                    results.append(result)

        # Sort results back to original order
        passage_order = {p.reference: i for i, p in enumerate(passages)}
        results.sort(key=lambda r: passage_order.get(r.passage.reference, 999))

        return results

    def _generate_cache_key(self, passages: List[BiblicalPassage], algorithms: List[str] = None) -> str:
        """Generate a cache key for the batch"""
        passage_refs = sorted([p.reference for p in passages])
        algo_key = "_".join(sorted(algorithms)) if algorithms else "all"
        return f"batch_{len(passages)}_{hash('_'.join(passage_refs))}_{algo_key}"

    def analyze_corpus_by_book(self, corpus: List[BiblicalPassage]) -> Dict[str, BatchAnalysisResult]:
        """Analyze corpus grouped by book"""
        books = {}
        for passage in corpus:
            if passage.book not in books:
                books[passage.book] = []
            books[passage.book].append(passage)

        book_results = {}
        for book_name, passages in books.items():
            print(f"Analyzing book: {book_name} ({len(passages)} passages)")
            result = self.analyze_batch(passages)
            book_results[book_name] = result

        return book_results

    def analyze_corpus_by_testament(self, corpus: List[BiblicalPassage]) -> Dict[str, BatchAnalysisResult]:
        """Analyze corpus grouped by testament"""
        testaments = {"Old": [], "New": []}
        for passage in corpus:
            if passage.testament in testaments:
                testaments[passage.testament].append(passage)

        testament_results = {}
        for testament, passages in testaments.items():
            if passages:  # Only analyze if there are passages
                print(f"Analyzing {testament} Testament ({len(passages)} passages)")
                result = self.analyze_batch(passages)
                testament_results[testament] = result

        return testament_results

    def find_patterns_across_batch(self, batch_result: BatchAnalysisResult) -> Dict[str, Any]:
        """Find patterns and themes across the entire batch"""
        if not batch_result.results:
            return {}

        # Aggregate themes across all passages
        all_themes = {}
        all_confidences = []

        for result in batch_result.results:
            thematic_analysis = result.dimension_results.get(AnalysisDimension.THEMATIC)
            if thematic_analysis:
                themes = thematic_analysis.findings.get("detected_themes", {})
                for theme, matches in themes.items():
                    if theme not in all_themes:
                        all_themes[theme] = []
                    all_themes[theme].extend(matches)

            all_confidences.append(result.get_average_confidence())

        # Find most common themes
        theme_frequencies = {theme: len(matches) for theme, matches in all_themes.items()}
        dominant_themes = sorted(theme_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]

        # Confidence distribution
        confidence_distribution = {
            "high": len([c for c in all_confidences if c >= 0.8]),
            "medium": len([c for c in all_confidences if 0.5 <= c < 0.8]),
            "low": len([c for c in all_confidences if c < 0.5])
        }

        return {
            "dominant_themes": dominant_themes,
            "theme_frequencies": theme_frequencies,
            "confidence_distribution": confidence_distribution,
            "average_batch_confidence": sum(all_confidences) / len(all_confidences) if all_confidences else 0.0,
            "total_unique_themes": len(all_themes)
        }

    def export_batch_results(self, batch_result: BatchAnalysisResult, filename: str):
        """Export batch analysis results to JSON"""
        data = {
            "version": __version__,
            "batch_analysis": {
                "passages_analyzed": batch_result.passages_analyzed,
                "total_insights": batch_result.total_insights,
                "average_confidence": batch_result.average_confidence,
                "processing_time": batch_result.processing_time,
                "batch_statistics": batch_result.batch_statistics,
                "timestamp": batch_result.timestamp
            },
            "individual_results": [
                {
                    "passage": {
                        "reference": r.passage.reference,
                        "text": r.passage.text,
                        "version": r.passage.version
                    },
                    "dimensions_analyzed": len(r.dimension_results),
                    "total_insights": r.get_total_insights(),
                    "total_findings": r.get_total_findings(),
                    "average_confidence": r.get_average_confidence(),
                    "multiplication_factor": r.multiplication_factor,
                    "synthesis": r.synthesis
                }
                for r in batch_result.results
            ]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def clear_cache(self):
        """Clear the batch analysis cache"""
        self.batch_cache.clear()

class ValidationEngine:
    """Validates analysis results with configurable rule-based validation"""

    def __init__(self):
        self.rules = {}  # name -> ValidationRule
        self.load_default_rules()

    def load_default_rules(self):
        """Load built-in validation rules"""
        default_rules = [
            ValidationRule(
                name="john_1_1_christological_check",
                description="John 1:1 should have high christological content",
                condition="result.passage.reference == 'John 1:1' and (result.dimension_results.get(AnalysisDimension.CHRISTOLOGICAL, DimensionalAnalysis(AnalysisDimension.CHRISTOLOGICAL, {}, [], 0)).findings.get('christological_density', 0) == 0)",
                severity="high",
                category="christological",
                message_template="John 1:1 is highly christological but scored 0 density",
                suggested_fix="Add contextual title detection for 'Word' (Logos)"
            ),
            ValidationRule(
                name="beginning_cross_reference_check",
                description="Passages with 'beginning' should reference Genesis 1:1",
                condition="'beginning' in result.passage.text.lower() and not any('genesis' in ref.get('reference', '').lower() if isinstance(ref, dict) else str(ref).lower() for ref in result.dimension_results.get(AnalysisDimension.CROSS_REFERENCE, DimensionalAnalysis(AnalysisDimension.CROSS_REFERENCE, {}, [], 0)).findings.get('cross_references', []))",
                severity="medium",
                category="cross_reference",
                enabled=False,  # Temporarily disabled due to eval context issues
                message_template="'beginning' should connect to Genesis 1:1",
                suggested_fix="Add Genesis 1:1 to cross-references for passages mentioning 'beginning'"
            ),
            ValidationRule(
                name="lexical_thematic_consistency",
                description="High lexical diversity should correlate with complex themes",
                condition="(result.dimension_results.get(AnalysisDimension.LEXICAL, DimensionalAnalysis(AnalysisDimension.LEXICAL, {}, [], 0)).findings.get('lexical_diversity', 0) > 0.6) and (result.dimension_results.get(AnalysisDimension.THEMATIC, DimensionalAnalysis(AnalysisDimension.THEMATIC, {}, [], 0)).findings.get('theme_count', 0) < 2)",
                severity="low",
                category="consistency",
                message_template="High lexical diversity ({lexical_diversity:.2f}) suggests complex content but only {theme_count} themes detected",
                suggested_fix="Review thematic analysis for additional theme detection"
            ),
            ValidationRule(
                name="temporal_eschatological_consistency",
                description="Eschatological content should have future temporal markers",
                condition="(result.dimension_results.get(AnalysisDimension.ESCHATOLOGICAL, DimensionalAnalysis(AnalysisDimension.ESCHATOLOGICAL, {}, [], 0)).findings.get('eschatological_density', 0) > 0.01) and (result.dimension_results.get(AnalysisDimension.TEMPORAL, DimensionalAnalysis(AnalysisDimension.TEMPORAL, {}, [], 0)).findings.get('tense_distribution', {}).get('future', 0) == 0)",
                severity="medium",
                category="temporal",
                message_template="Eschatological content (density: {eschatological_density:.3f}) but no future tense markers",
                suggested_fix="Check for future-oriented language in eschatological passages"
            )
        ]

        for rule in default_rules:
            self.rules[rule.name] = rule

    def load_rules_from_file(self, filepath: str):
        """Load validation rules from JSON file"""
        try:
            with open(filepath, 'r') as f:
                rules_data = json.load(f)

            for rule_data in rules_data.get('rules', []):
                rule = ValidationRule(**rule_data)
                self.rules[rule.name] = rule

        except FileNotFoundError:
            print(f"Validation rules file not found: {filepath}")
        except json.JSONDecodeError:
            print(f"Invalid JSON in validation rules file: {filepath}")

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str):
        """Remove a validation rule"""
        if rule_name in self.rules:
            del self.rules[rule_name]

    def validate_analysis(self, result: MultiDimensionalResult) -> Dict[str, Any]:
        """Run rule-based validation checks on analysis results"""
        issues = []
        corrections = []

        # Evaluate each enabled rule
        for rule in self.rules.values():
            if not rule.enabled:
                continue

            try:
                # Create evaluation context
                context = {
                    'result': result,
                    'AnalysisDimension': AnalysisDimension,
                    'DimensionalAnalysis': DimensionalAnalysis,
                    'len': len,
                    'any': any,
                    'all': all,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'str': str
                }

                # Evaluate the condition
                condition_met = eval(rule.condition, {"__builtins__": {}}, context)

                if condition_met:
                    # Format message with template variables
                    message = rule.message_template
                    if '{' in message:
                        # Extract values for template
                        lexical_diversity = result.dimension_results.get(AnalysisDimension.LEXICAL, DimensionalAnalysis(AnalysisDimension.LEXICAL, {}, [], 0)).findings.get('lexical_diversity', 0)
                        theme_count = result.dimension_results.get(AnalysisDimension.THEMATIC, DimensionalAnalysis(AnalysisDimension.THEMATIC, {}, [], 0)).findings.get('theme_count', 0)
                        eschatological_density = result.dimension_results.get(AnalysisDimension.ESCHATOLOGICAL, DimensionalAnalysis(AnalysisDimension.ESCHATOLOGICAL, {}, [], 0)).findings.get('eschatological_density', 0)

                        message = message.format(
                            lexical_diversity=lexical_diversity,
                            theme_count=theme_count,
                            eschatological_density=eschatological_density
                        )

                    issues.append({
                        "rule_name": rule.name,
                        "type": rule.category,
                        "description": message,
                        "severity": rule.severity,
                        "suggested_fix": rule.suggested_fix
                    })

            except Exception as e:
                # Log evaluation errors but continue
                print(f"Error evaluating rule {rule.name}: {e}")

        return {
            "validation_passed": len(issues) == 0,
            "issues_found": len(issues),
            "issues": issues,
            "corrections_applied": corrections,
            "rules_evaluated": len([r for r in self.rules.values() if r.enabled])
        }

# Algorithm Library v0.0.4

def lexical_analysis(passage: BiblicalPassage) -> Dict[str, Any]:
    """Enhanced lexical analysis with spaCy NLP features"""
    words = passage.get_cached_words()
    lemmas = passage.get_lemmas()
    pos_tags = passage.get_pos_tags()

    # Build frequency distributions
    word_freq = {}
    lemma_freq = {}
    pos_freq = {}

    for word in words:
        word_lower = word.lower()
        word_freq[word_lower] = word_freq.get(word_lower, 0) + 1

    for lemma in lemmas:
        lemma_freq[lemma] = lemma_freq.get(lemma, 0) + 1

    for pos in pos_tags:
        pos_freq[pos] = pos_freq.get(pos, 0) + 1

    # Calculate metrics
    unique_words = len(word_freq)
    unique_lemmas = len(lemma_freq)
    total_words = len(words)
    avg_word_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0
    hapax_legomena = [word for word, count in word_freq.items() if count == 1]

    # spaCy-enhanced metrics
    lexical_density = unique_lemmas / total_words if total_words > 0 else 0
    pos_diversity = len(pos_freq) / 36.0 if pos_freq else 0  # Universal POS tag set has ~36 tags

    return {
        "findings": {
            "word_count": total_words,
            "unique_words": unique_words,
            "unique_lemmas": unique_lemmas,
            "lexical_diversity": unique_words / total_words if total_words > 0 else 0,
            "lexical_density": lexical_density,  # Lemmas per word
            "average_word_length": round(avg_word_length, 2),
            "hapax_legomena_count": len(hapax_legomena),
            "pos_distribution": pos_freq,
            "pos_diversity": round(pos_diversity, 3),
            "most_frequent_words": sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_frequent_lemmas": sorted(lemma_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        },
        "insights": [
            f"Passage contains {total_words} words with {unique_words} unique words ({unique_lemmas} unique lemmas)",
            f"Lexical diversity: {unique_words / total_words:.2f}, Lexical density: {lexical_density:.2f}",
            f"POS diversity: {pos_diversity:.2f} (higher = more varied grammar)",
            f"Average word length: {avg_word_length:.1f} characters",
            f"Hapax legomena: {len(hapax_legomena)} words appearing only once"
        ],
        "confidence": 1.0
    }

def thematic_extraction(passage: BiblicalPassage) -> Dict[str, Any]:
    """Enhanced thematic analysis with regex patterns and synonym dictionary"""
    # Initialize synonym dictionary
    synonym_dict = SynonymDictionary()

    # Regex patterns for more sophisticated theme detection
    theme_patterns = {
        "creation": [
            r'\bcreat\w*\b',  # create, created, creating, etc.
            r'\bmade?\b',     # made, make
            r'\bbeginning\b',
            r'\bheaven\b',
            r'\bearth\b',
            r'\bform\w*\b',   # form, formed, forming
            r'\bestablish\w*\b'
        ],
        "salvation": [
            r'\bsav\w*\b',    # save, saved, saving, salvation
            r'\bredeem\w*\b', # redeem, redeemed, redemption
            r'\bforgiv\w*\b', # forgive, forgiven, forgiveness
            r'\bgrace\b',
            r'\bdeliver\w*\b', # deliver, delivered, deliverance
            r'\brescu\w*\b'   # rescue, rescued
        ],
        "kingdom": [
            r'\bkingdom\b',
            r'\bking\w*\b',   # king, kings, kingdom
            r'\brul\w*\b',    # rule, ruling, ruler
            r'\breign\w*\b',  # reign, reigning
            r'\bthrone\b',
            r'\bgovern\w*\b', # govern, government
            r'\bauthority\b'
        ],
        "love": [
            r'\blov\w*\b',    # love, loved, loving
            r'\bbeloved\b',
            r'\bdear\w*\b',   # dear, dearly
            r'\bcherish\w*\b',
            r'\bcompassion\b',
            r'\bmerc\w*\b',   # mercy, merciful
            r'\baffection\b'
        ],
        "faith": [
            r'\bfaith\w*\b',  # faith, faithful, faithfulness
            r'\bbeliev\w*\b', # believe, believed, believing
            r'\btrust\w*\b',  # trust, trusted, trusting
            r'\bhope\w*\b',   # hope, hoped, hoping
            r'\bconfid\w*\b'  # confidence, confident
        ],
        "holiness": [
            r'\bholy\b',
            r'\bsacred\b',
            r'\bpure\b',
            r'\brighteous\b',
            r'\bsanctif\w*\b', # sanctify, sanctified
            r'\bconsecrat\w*\b',
            r'\bdivine\b'
        ],
        "wisdom": [
            r'\bwis\w*\b',    # wise, wisdom, wisely
            r'\bunderstand\w*\b',
            r'\bknowledg\w*\b', # knowledge, knowing
            r'\bdiscern\w*\b',
            r'\binsight\b',
            r'\bintellig\w*\b' # intelligence, intelligent
        ],
        "justice": [
            r'\bjust\w*\b',   # justice, just, justify
            r'\brighteous\b',
            r'\bjudg\w*\b',   # judge, judgment, judging
            r'\bfair\w*\b',   # fair, fairness
            r'\bequit\w*\b',  # equity, equitable
            r'\blaw\w*\b',    # law, lawful
            r'\bvindicat\w*\b'
        ]
    }

    text_lower = passage.get_cached_text_lower()
    lemmas = passage.get_lemmas()  # Use spaCy lemmas for better matching
    detected_themes = {}
    total_theme_matches = 0
    synonym_matches = {}

    for theme, patterns in theme_patterns.items():
        matches = []
        for pattern in patterns:
            found_matches = re.findall(pattern, text_lower)
            if found_matches:
                matches.extend(found_matches)

        # Also check for synonyms of theme keywords using lemmas
        theme_keywords = [theme]  # Add theme name itself
        # Add common keywords for each theme
        theme_base_keywords = {
            "creation": ["create", "beginning", "heaven", "earth"],
            "salvation": ["save", "salvation", "redeem", "grace"],
            "kingdom": ["kingdom", "king", "rule", "reign"],
            "love": ["love", "beloved", "compassion"],
            "faith": ["faith", "believe", "trust"],
            "holiness": ["holy", "sacred", "pure", "righteous"],
            "wisdom": ["wise", "wisdom", "understanding"],
            "justice": ["justice", "righteous", "judge"]
        }
        if theme in theme_base_keywords:
            theme_keywords.extend(theme_base_keywords[theme])

        # Check both original text and lemmas for synonyms
        synonym_matches[theme] = synonym_dict.find_synonym_matches(text_lower, theme_keywords)
        lemma_synonym_matches = synonym_dict.find_synonym_matches(' '.join(lemmas), theme_keywords)

        # Merge synonym matches from both text and lemmas
        for key in lemma_synonym_matches:
            if key in synonym_matches[theme]:
                synonym_matches[theme][key].extend(lemma_synonym_matches[key])
                synonym_matches[theme][key] = list(set(synonym_matches[theme][key]))  # Remove duplicates
            else:
                synonym_matches[theme][key] = lemma_synonym_matches[key]

        # Combine regex matches with synonym matches
        all_matches = matches[:]
        for keyword_matches in synonym_matches[theme].values():
            all_matches.extend(keyword_matches)

        if all_matches:
            # Remove duplicates while preserving order
            unique_matches = list(dict.fromkeys(all_matches))
            detected_themes[theme] = unique_matches
            total_theme_matches += len(unique_matches)

    dominant_themes = sorted(detected_themes.keys(), key=lambda t: len(detected_themes[t]), reverse=True)

    return {
        "findings": {
            "detected_themes": detected_themes,
            "theme_count": len(detected_themes),
            "total_theme_matches": total_theme_matches,
            "dominant_themes": dominant_themes[:3],
            "theme_density": total_theme_matches / len(passage.get_cached_words()) if passage.get_cached_words() else 0,
            "synonym_matches": synonym_matches
        },
        "insights": [
            f"Detected {len(detected_themes)} theological themes using regex and synonym matching",
            f"Dominant themes: {', '.join(dominant_themes[:3])}",
            f"Theme density: {total_theme_matches / len(passage.get_cached_words()):.3f} matches per word",
            f"Synonym-enhanced matching found additional connections in {len([s for s in synonym_matches.values() if s])} themes"
        ],
        "confidence": 0.95  # Increased confidence due to synonym enhancement
    }

def structural_analysis(passage: BiblicalPassage) -> Dict[str, Any]:
    """Structural analysis - sentence and clause patterns"""
    text = passage.text
    sentences = [s.strip() for s in text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
    words = text.split()

    # Basic structural metrics
    sentence_count = len(sentences)
    avg_sentence_length = len(words) / sentence_count if sentence_count > 0 else 0

    # Question and exclamation detection
    questions = text.count('?')
    exclamations = text.count('!')

    # Parallelism detection (simple repetition)
    word_repetitions = {}
    for i in range(len(words) - 1):
        pair = f"{words[i]} {words[i+1]}"
        word_repetitions[pair] = word_repetitions.get(pair, 0) + 1

    return {
        "findings": {
            "sentence_count": sentence_count,
            "average_sentence_length": round(avg_sentence_length, 1),
            "question_count": questions,
            "exclamation_count": exclamations,
            "word_repetitions": word_repetitions,
            "complexity_score": round(avg_sentence_length * (1 + questions + exclamations), 2)
        },
        "insights": [
            f"Passage contains {sentence_count} sentences with average length {avg_sentence_length:.1f} words",
            f"Contains {questions} questions and {exclamations} exclamations",
            f"Structural complexity score: {avg_sentence_length * (1 + questions + exclamations):.1f}"
        ],
        "confidence": 0.9
    }

def christological_analysis(passage: BiblicalPassage) -> Dict[str, Any]:
    """Christological analysis - Christ-centered content detection"""
    christ_titles = ["christ", "jesus", "son of god", "son of man", "messiah", "savior", "lord", "king", "lamb", "shepherd"]
    christ_actions = ["came", "died", "rose", "ascended", "will come", "saves", "heals", "teaches", "forgives"]

    text_lower = passage.text.lower()
    detected_titles = [title for title in christ_titles if title in text_lower]
    detected_actions = [action for action in christ_actions if action in text_lower]

    # Contextual Christ titles (for verses like John 1:1 where "Word" = Logos)
    contextual_titles = {
        "word": ["beginning", "god", "with god"],  # John 1:1 pattern
        "light": ["darkness", "world", "shine"],    # John 1:4-5 pattern
        "bread": ["life", "heaven", "come down"],   # John 6:35 pattern
        "way": ["truth", "life", "father"]          # John 14:6 pattern
    }

    detected_contextual = []
    for title, context_words in contextual_titles.items():
        if title in text_lower:
            context_match = sum(1 for word in context_words if word in text_lower)
            if context_match >= 2:  # Require strong contextual evidence
                detected_contextual.append({
                    "title": title,
                    "context_strength": context_match / len(context_words),
                    "interpretation": f"'{title}' in context of {', '.join([w for w in context_words if w in text_lower])}"
                })
                # Add to main titles list if not already there
                if title not in detected_titles:
                    detected_titles.append(title)

    # Christological density (include contextual titles)
    christ_words = sum(text_lower.count(title) for title in christ_titles)
    contextual_words = sum(1 for ctx in detected_contextual for _ in ctx["interpretation"].split())
    total_words = len(text_lower.split())
    density = (christ_words + contextual_words) / total_words if total_words > 0 else 0

    focus_intensity = "low"
    if density > 0.05:
        focus_intensity = "high"
    elif density > 0.02:
        focus_intensity = "medium"

    return {
        "findings": {
            "christ_titles": detected_titles,
            "contextual_christ_titles": detected_contextual,
            "christ_actions": detected_actions,
            "christological_density": round(density, 4),
            "focus_intensity": focus_intensity,
            "title_count": len(detected_titles),
            "contextual_title_count": len(detected_contextual),
            "action_count": len(detected_actions)
        },
        "insights": [
            f"Detected {len(detected_titles)} Christ titles: {', '.join(detected_titles)}",
            f"Contextual Christ titles: {len(detected_contextual)} (e.g., {', '.join([ctx['title'] for ctx in detected_contextual[:2]])})" if detected_contextual else "No contextual Christ titles detected",
            f"Christological focus intensity: {focus_intensity} (density: {density:.3f})",
            f"Christ-related actions: {', '.join(detected_actions)}"
        ],
        "confidence": 0.9
    }

@dataclass
class CrossReferenceLink:
    """Enhanced cross-reference with multiple detection methods"""
    reference: str
    relationship_type: str  # "direct_quote", "parallel", "thematic_echo", "typological"
    strength: float
    detection_method: str
    evidence: Dict[str, Any]

def cross_reference_detection(passage: BiblicalPassage) -> Dict[str, Any]:
    """Enhanced cross-reference detection with n-gram quotation detection and allusion strength scoring"""
    text_lower = passage.text.lower()
    words = passage.get_cached_words()

    # Method 1: Structural similarity (opening phrases)
    opening_patterns = {
        "Genesis 1:1": {"phrase": "in the beginning", "strength": 1.0},
        "Proverbs 8:22": {"phrase": "beginning", "context": ["wisdom", "way"]},
        "1 John 1:1": {"phrase": "beginning", "context": ["word", "life"]}
    }

    # Method 2: Theological concept clustering
    concept_clusters = {
        "divine_preexistence": ["Genesis 1:1", "Proverbs 8:22-31", "John 1:1", "Colossians 1:15-17"],
        "word_as_creator": ["Genesis 1:3", "Psalm 33:6", "John 1:1-3", "Hebrews 11:3"],
        "god_with_god": ["Genesis 1:26", "Proverbs 8:30", "John 1:1", "John 17:5"]
    }

    # Method 3: Simple keyword-based (legacy)
    reference_patterns = {
        "genesis_1": ["beginning", "create", "heaven", "earth"],
        "exodus_20": ["commandments", "ten", "thou shalt"],
        "psalm_23": ["shepherd", "green pastures", "still waters"],
        "john_3_16": ["god so loved", "gave his son", "eternal life"],
        "matthew_5": ["blessed", "poor in spirit", "kingdom of heaven"]
    }

    # Method 4: N-gram quotation detection (NEW)
    ngram_references = {
        2: {  # Bigrams
            "in the beginning": ["Genesis 1:1", "Proverbs 8:22", "John 1:1"],
            "word of god": ["Hebrews 4:12", "2 Timothy 2:9", "1 Peter 1:23"],
            "kingdom of heaven": ["Matthew 5:3", "Matthew 5:10", "Matthew 5:19"],
            "son of man": ["Daniel 7:13", "Matthew 8:20", "Matthew 12:40"]
        },
        3: {  # Trigrams
            "in the beginning god": ["Genesis 1:1"],
            "word was with god": ["John 1:1"],
            "word became flesh": ["John 1:14"],
            "love one another": ["John 13:34", "1 John 3:11"],
            "blessed are the": ["Matthew 5:3", "Matthew 5:4", "Matthew 5:5"]
        },
        4: {  # Quadgrams
            "in the beginning was the word": ["John 1:1"],
            "the word became flesh and": ["John 1:14"],
            "god so loved the world": ["John 3:16"],
            "blessed are the poor in spirit": ["Matthew 5:3"]
        }
    }

    links = []

    # Detect opening phrase parallels
    for ref, pattern in opening_patterns.items():
        if pattern["phrase"] in text_lower:
            context_match = 0
            if "context" in pattern:
                context_match = sum(1 for word in pattern["context"] if word in text_lower)

            base_strength = pattern.get("strength", 0.8)
            strength = base_strength
            if context_match > 0:
                strength += (context_match * 0.2)

            links.append(CrossReferenceLink(
                reference=ref,
                relationship_type="structural_parallel",
                strength=min(strength, 1.0),
                detection_method="opening_phrase_analysis",
                evidence={"phrase": pattern["phrase"], "context_matches": context_match}
            ))

    # Detect concept cluster memberships
    for concept, references in concept_clusters.items():
        concept_keywords = {
            "divine_preexistence": ["beginning", "was", "before"],
            "word_as_creator": ["word", "made", "create", "beginning"],
            "god_with_god": ["god", "with", "was"]
        }

        if concept in concept_keywords:
            keywords = concept_keywords[concept]
            keyword_matches = sum(1 for kw in keywords if kw in text_lower)

            if keyword_matches >= len(keywords) - 1:
                for ref in references:
                    if ref != passage.reference:
                        links.append(CrossReferenceLink(
                            reference=ref,
                            relationship_type="conceptual_cluster",
                            strength=keyword_matches / len(keywords),
                            detection_method="theological_concept_matching",
                            evidence={"concept": concept, "matched_keywords": keyword_matches}
                        ))

    # Legacy keyword-based detection
    for ref, keywords in reference_patterns.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches >= 2:
            strength = matches / len(keywords)
            links.append(CrossReferenceLink(
                reference=ref,
                relationship_type="thematic_echo",
                strength=strength,
                detection_method="keyword_matching",
                evidence={"matched_keywords": [kw for kw in keywords if kw in text_lower]}
            ))

    # N-gram quotation detection (NEW)
    for n in [4, 3, 2]:  # Check longer n-grams first
        if n in ngram_references:
            for ngram, references in ngram_references[n].items():
                ngram_words = ngram.split()
                if len(words) >= n:
                    # Check for consecutive n-gram matches
                    for i in range(len(words) - n + 1):
                        window = ' '.join(words[i:i+n]).lower()
                        if window == ngram:
                            # Calculate allusion strength based on n-gram length and context
                            base_strength = n * 0.2  # Longer n-grams = stronger allusions
                            context_bonus = 0.0

                            # Check surrounding context (5 words before and after)
                            start_idx = max(0, i - 5)
                            end_idx = min(len(words), i + n + 5)
                            context_window = ' '.join(words[start_idx:end_idx]).lower()

                            # Look for additional biblical markers in context
                            biblical_markers = ["thus says", "hear the word", "word of the lord", "scripture says"]
                            context_bonus += sum(1 for marker in biblical_markers if marker in context_window) * 0.1

                            strength = min(base_strength + context_bonus, 1.0)

                            for ref in references:
                                if ref != passage.reference:
                                    links.append(CrossReferenceLink(
                                        reference=ref,
                                        relationship_type="direct_quotation" if n >= 3 else "quotation_allusion",
                                        strength=strength,
                                        detection_method="n_gram_quotation_detection",
                                        evidence={
                                            "ngram": ngram,
                                            "ngram_length": n,
                                            "position": i,
                                            "context_bonus": context_bonus
                                        }
                                    ))

    # Allusion strength scoring (enhance existing links)
    for link in links:
        # Calculate overall allusion strength based on multiple factors
        base_strength = link.strength

        # Factor 1: Detection method reliability
        method_weights = {
            "n_gram_quotation_detection": 1.2,  # Highest weight for direct n-gram matches
            "opening_phrase_analysis": 1.1,
            "theological_concept_matching": 1.0,
            "keyword_matching": 0.8
        }
        method_multiplier = method_weights.get(link.detection_method, 1.0)

        # Factor 2: Evidence strength
        evidence_strength = 1.0
        if link.detection_method == "n_gram_quotation_detection":
            ngram_length = link.evidence.get("ngram_length", 2)
            evidence_strength = ngram_length / 4.0  # Normalize to quadgram
        elif link.detection_method == "keyword_matching":
            matched_count = len(link.evidence.get("matched_keywords", []))
            evidence_strength = min(matched_count / 3.0, 1.0)  # Up to 3 keywords

        # Factor 3: Contextual relevance (check if reference is from same testament/book)
        contextual_relevance = 1.0
        if hasattr(passage, 'testament') and link.reference:
            # Simple heuristic: same testament gets bonus
            ref_testament = "Old" if any(book in link.reference for book in
                                        ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
                                         "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
                                         "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
                                         "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
                                         "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
                                         "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
                                         "Haggai", "Zechariah", "Malachi"]) else "New"
            if ref_testament == passage.testament:
                contextual_relevance = 1.1

        # Calculate final allusion strength
        link.strength = min(base_strength * method_multiplier * evidence_strength * contextual_relevance, 1.0)

    # Sort by enhanced strength and take top references
    links.sort(key=lambda x: x.strength, reverse=True)
    top_links = links[:7]  # Increased from 5 to allow more n-gram detections

    return {
        "findings": {
            "cross_references": [
                {
                    "reference": link.reference,
                    "type": link.relationship_type,
                    "strength": round(link.strength, 3),
                    "method": link.detection_method,
                    "evidence": link.evidence
                }
                for link in top_links
            ],
            "reference_count": len(top_links),
            "strongest_connection": {
                "reference": top_links[0].reference,
                "type": top_links[0].relationship_type,
                "strength": round(top_links[0].strength, 3)
            } if top_links else None,
            "detection_methods_used": list(set(link.detection_method for link in top_links)),
            "quotation_detections": len([l for l in top_links if "quotation" in l.relationship_type])
        },
        "insights": [
            f"Detected {len(top_links)} cross-references using {len(set(link.detection_method for link in top_links))} methods",
            f"Strongest connection: {top_links[0].reference if top_links else 'None'} (strength: {top_links[0].strength:.3f})" if top_links else "No strong connections found",
            f"N-gram quotation detections: {len([l for l in top_links if l.detection_method == 'n_gram_quotation_detection'])}"
        ],
        "confidence": 0.8,  # Increased confidence due to n-gram detection
        "links": [
            LinkedPassage(
                reference=link.reference,
                relationship=link.relationship_type,
                insight=f"Connected via {link.detection_method}: {link.evidence}"
            )
            for link in top_links
        ]
    }

def literary_analysis(passage: BiblicalPassage) -> Dict[str, Any]:
    """Literary analysis - poetic and rhetorical devices"""
    text_lower = passage.text.lower()
    words = text_lower.split()

    # Repetition detection
    repetition_patterns = {}
    for i in range(len(words) - 1):
        pair = f"{words[i]} {words[i+1]}"
        repetition_patterns[pair] = repetition_patterns.get(pair, 0) + 1

    significant_repetitions = {k: v for k, v in repetition_patterns.items() if v > 1}

    # Imagery detection (sensory words)
    sensory_words = {
        "visual": ["see", "light", "dark", "bright", "color", "appear"],
        "auditory": ["hear", "sound", "voice", "cry", "speak", "call"],
        "tactile": ["touch", "feel", "warm", "cold", "soft", "hard"],
        "olfactory": ["smell", "fragrant", "odor", "sweet"],
        "gustatory": ["taste", "sweet", "bitter", "eat", "drink"]
    }

    imagery_detected = {}
    for sense, words_list in sensory_words.items():
        matches = [w for w in words_list if w in text_lower]
        if matches:
            imagery_detected[sense] = matches

    # Metaphor/simile detection (simple)
    metaphor_indicators = ["like", "as", "is", "are", "becomes"]
    metaphor_count = sum(1 for word in metaphor_indicators if word in words)

    literary_richness = len(significant_repetitions) + len(imagery_detected) + metaphor_count

    return {
        "findings": {
            "repetition_patterns": significant_repetitions,
            "imagery_detected": imagery_detected,
            "metaphor_indicators": metaphor_count,
            "literary_richness_score": literary_richness,
            "imagery_senses": list(imagery_detected.keys())
        },
        "insights": [
            f"Literary richness score: {literary_richness}",
            f"Imagery in {len(imagery_detected)} senses: {', '.join(imagery_detected.keys())}",
            f"Repetition patterns detected: {len(significant_repetitions)}"
        ],
        "confidence": 0.75
    }

def ethical_analysis(passage: BiblicalPassage) -> Dict[str, Any]:
    """Ethical analysis with spaCy POS tagging for imperative detection"""
    text_lower = passage.text.lower()
    doc = passage.get_spacy_doc()

    # Enhanced imperative detection using spaCy POS
    imperative_count = 0
    if doc:
        # Count imperative verbs (base form verbs that are commands)
        for token in doc:
            if token.pos_ == "VERB" and token.morph.get("VerbForm") == ["Inf"]:  # Infinitive as imperative
                imperative_count += 1
            elif token.pos_ == "VERB" and token.dep_ in ["ROOT", "ccomp"] and not token.morph.get("Tense"):
                # Simple heuristic for imperative verbs
                imperative_count += 1
    else:
        # Fallback to keyword-based detection
        imperatives = ["shall", "must", "should", "ought", "do not", "thou shalt", "you shall"]
        imperative_count = sum(1 for imp in imperatives if imp in text_lower)

    # Virtue and vice detection (enhanced with lemmas)
    virtues = ["love", "justice", "mercy", "compassion", "faithfulness", "truth", "righteousness", "holiness"]
    vices = ["hate", "injustice", "cruelty", "unfaithfulness", "lies", "wickedness", "sin"]

    lemmas = passage.get_lemmas()
    lemma_text = ' '.join(lemmas)

    detected_virtues = [v for v in virtues if v in text_lower or v in lemma_text]
    detected_vices = [v for v in vices if v in text_lower or v in lemma_text]

    # Moral density
    moral_words = len(detected_virtues) + len(detected_vices) + imperative_count
    total_words = len(passage.get_cached_words())
    moral_density = moral_words / total_words if total_words > 0 else 0

    # Prescriptive vs descriptive (enhanced)
    prescriptive_indicators = imperative_count + len(detected_virtues)
    descriptive_indicators = len(detected_vices)
    # Check for narrative/storytelling indicators
    narrative_indicators = ["story", "narrative", "told", "happened", "occurred"]
    descriptive_indicators += sum(1 for ind in narrative_indicators if ind in lemma_text)

    content_type = "balanced"
    if prescriptive_indicators > descriptive_indicators * 1.5:
        content_type = "prescriptive"
    elif descriptive_indicators > prescriptive_indicators * 1.5:
        content_type = "descriptive"

    return {
        "findings": {
            "imperative_count": imperative_count,
            "detected_virtues": detected_virtues,
            "detected_vices": detected_vices,
            "moral_density": round(moral_density, 4),
            "content_type": content_type,
            "virtue_count": len(detected_virtues),
            "vice_count": len(detected_vices),
            "prescriptive_score": prescriptive_indicators,
            "descriptive_score": descriptive_indicators
        },
        "insights": [
            f"Ethical content type: {content_type} (moral density: {moral_density:.3f})",
            f"Detected {len(detected_virtues)} virtues and {len(detected_vices)} vices",
            f"Imperative statements: {imperative_count} (using POS tagging)" if doc else f"Imperative statements: {imperative_count} (keyword-based)",
            f"Prescriptive vs Descriptive: {prescriptive_indicators} vs {descriptive_indicators}"
        ],
        "confidence": 0.9 if doc else 0.8  # Higher confidence with POS tagging
    }

def temporal_analysis(passage: BiblicalPassage) -> Dict[str, Any]:
    """Temporal analysis - time-based patterns and sequences"""
    text_lower = passage.text.lower()

    # Time indicators
    temporal_markers = {
        "past": ["was", "were", "had", "did", "came", "went", "began", "created", "made"],
        "present": ["is", "are", "has", "do", "come", "go", "begin", "create", "make"],
        "future": ["will", "shall", "would", "should", "may", "might", "can", "could"]
    }

    # Sequence words
    sequence_words = ["then", "after", "before", "when", "while", "during", "next", "finally", "lastly", "first"]

    # Time references
    time_references = ["day", "night", "morning", "evening", "year", "month", "week", "hour", "time", "season"]

    tense_distribution = {}
    for tense, words in temporal_markers.items():
        # Count ALL occurrences of each marker word, not just presence
        count = sum(text_lower.count(word) for word in words)
        tense_distribution[tense] = count

    sequence_count = sum(1 for word in sequence_words if word in text_lower)
    time_ref_count = sum(1 for ref in time_references if ref in text_lower)

    # Temporal flow assessment
    total_temporal_words = sum(tense_distribution.values())
    temporal_density = total_temporal_words / len(passage.text.split()) if passage.text.split() else 0

    # Dominant tense
    dominant_tense = max(tense_distribution.keys(), key=lambda k: tense_distribution[k]) if any(tense_distribution.values()) else "neutral"

    return {
        "findings": {
            "tense_distribution": tense_distribution,
            "sequence_indicators": sequence_count,
            "time_references": time_ref_count,
            "temporal_density": round(temporal_density, 4),
            "dominant_tense": dominant_tense,
            "temporal_flow_score": round((sequence_count + time_ref_count) / max(1, len(passage.text.split())), 4)
        },
        "insights": [
            f"Temporal density: {temporal_density:.3f} (words per total words)",
            f"Dominant tense: {dominant_tense} ({tense_distribution[dominant_tense]} indicators)",
            f"Sequence indicators: {sequence_count}, Time references: {time_ref_count}",
            f"Temporal flow score: {((sequence_count + time_ref_count) / max(1, len(passage.text.split()))):.3f}"
        ],
        "confidence": 0.85
    }

def eschatological_analysis(passage: BiblicalPassage) -> Dict[str, Any]:
    """Eschatological analysis - end-times themes and prophecy"""
    text_lower = passage.text.lower()

    # Eschatological themes
    eschatological_themes = {
        "judgment": ["judge", "judgment", "condemn", "wrath", "anger"],
        "kingdom": ["kingdom", "reign", "throne", "rule", "dominion"],
        "return": ["return", "come back", "second coming", "appear", "reveal"],
        "resurrection": ["resurrection", "rise", "raised", "alive", "eternal"],
        "new_creation": ["new heaven", "new earth", "renew", "restore", "make new"],
        "final_events": ["end", "last", "final", "consummation", "fulfillment"]
    }

    # Prophetic markers
    prophetic_markers = ["prophecy", "prophet", "vision", "dream", "oracle", "thus says", "hear the word"]

    detected_themes = {}
    total_eschatological_matches = 0

    for theme, keywords in eschatological_themes.items():
        matches = [kw for kw in keywords if kw in text_lower]
        if matches:
            detected_themes[theme] = matches
            total_eschatological_matches += len(matches)

    prophetic_count = sum(1 for marker in prophetic_markers if marker in text_lower)

    # Eschatological intensity
    eschatological_density = total_eschatological_matches / len(passage.text.split()) if passage.text.split() else 0

    # Classification
    if eschatological_density > 0.03:
        eschatological_intensity = "high"
    elif eschatological_density > 0.01:
        eschatological_intensity = "medium"
    else:
        eschatological_intensity = "low"

    return {
        "findings": {
            "detected_eschatological_themes": detected_themes,
            "eschatological_theme_count": len(detected_themes),
            "total_eschatological_matches": total_eschatological_matches,
            "prophetic_markers": prophetic_count,
            "eschatological_density": round(eschatological_density, 4),
            "eschatological_intensity": eschatological_intensity
        },
        "insights": [
            f"Eschatological intensity: {eschatological_intensity} (density: {eschatological_density:.3f})",
            f"Detected eschatological themes: {len(detected_themes)}",
            f"Prophetic markers: {prophetic_count}"
        ],
        "confidence": 0.8
    }

def historical_analysis(passage: BiblicalPassage) -> Dict[str, Any]:
    """Historical analysis with spaCy NER and enhanced cultural detection"""
    text_lower = passage.text.lower()
    lemmas = passage.get_lemmas()
    lemma_text = ' '.join(lemmas)

    # Use spaCy NER for entity recognition
    named_entities = passage.get_named_entities()
    person_entities = [ent for ent in named_entities if ent['label'] == 'PERSON']
    place_entities = [ent for ent in named_entities if ent['label'] in ['GPE', 'LOC', 'FAC']]

    # Historical figures and places (expanded list)
    historical_figures = ["abraham", "moses", "david", "solomon", "isaiah", "jeremiah", "paul", "peter",
                         "jesus", "john", "mary", "joseph", "adam", "eve", "noah", "jacob", "esau"]
    places = ["jerusalem", "egypt", "babylon", "rome", "nazareth", "galilee", "judea", "canaan",
             "sinai", "zion", "temple", "synagogue", "jordan"]

    # Cultural practices (expanded)
    cultural_practices = ["sacrifice", "offering", "temple", "synagogue", "festival", "sabbath",
                         "circumcision", "baptism", "prayer", "fasting", "tithe", "covenant"]

    # Historical time periods and references
    time_periods = ["ancient", "days", "generations", "forever", "eternal", "covenant",
                   "beginning", "creation", "exodus", "kingdom", "exile", "return"]

    # Check both original text and lemmas
    figures_mentioned = [fig for fig in historical_figures if fig in text_lower or fig in lemma_text]
    places_mentioned = [place for place in places if place in text_lower or place in lemma_text]
    practices_mentioned = [prac for prac in cultural_practices if prac in text_lower or prac in lemma_text]
    periods_mentioned = [per for per in time_periods if per in text_lower or per in lemma_text]

    # Add NER-detected entities
    for person in person_entities:
        person_name = person['text'].lower()
        if person_name not in figures_mentioned:
            figures_mentioned.append(person_name)

    for place in place_entities:
        place_name = place['text'].lower()
        if place_name not in places_mentioned:
            places_mentioned.append(place_name)

    # Historical context score
    historical_elements = len(figures_mentioned) + len(places_mentioned) + len(practices_mentioned) + len(periods_mentioned)
    total_words = len(passage.get_cached_words())
    historical_density = historical_elements / total_words if total_words > 0 else 0

    # Enhanced context type classification
    if historical_density > 0.05 or len(person_entities) > 2:
        context_type = "strongly_historical"
    elif historical_density > 0.025 or len(person_entities) > 0:
        context_type = "historically_rooted"
    else:
        context_type = "timeless_universal"

    return {
        "findings": {
            "historical_figures": figures_mentioned,
            "places_mentioned": places_mentioned,
            "cultural_practices": practices_mentioned,
            "time_periods": periods_mentioned,
            "named_entities_detected": named_entities,
            "person_entities": person_entities,
            "place_entities": place_entities,
            "historical_density": round(historical_density, 4),
            "context_type": context_type,
            "historical_elements_count": historical_elements
        },
        "insights": [
            f"Historical context: {context_type} (density: {historical_density:.3f})",
            f"Named entities: {len(named_entities)} total ({len(person_entities)} persons, {len(place_entities)} places)",
            f"Historical figures: {len(figures_mentioned)}, Places: {len(places_mentioned)}",
            f"Cultural practices: {len(practices_mentioned)}, Time periods: {len(periods_mentioned)}"
        ],
        "confidence": 0.85 if named_entities else 0.75  # Higher confidence with NER
    }

# Demo usage
if __name__ == "__main__":
    print(f"Bible Algorithmic Project - Framework v{__version__}")

    # Create framework
    framework = AlgorithmicFramework()

    # Register algorithms as plugins (v0.0.6 plugin architecture)
    framework.register_algorithm(
        "lexical_analysis", lexical_analysis,
        category="lexical", description="Word patterns and statistical analysis",
        tags=["language", "statistics", "vocabulary"]
    )
    framework.register_algorithm(
        "thematic_extraction", thematic_extraction,
        category="thematic", description="Theological concept detection with regex",
        tags=["theology", "concepts", "regex"]
    )
    framework.register_algorithm(
        "structural_analysis", structural_analysis,
        category="structural", description="Sentence and clause pattern analysis",
        tags=["structure", "syntax", "grammar"]
    )
    framework.register_algorithm(
        "christological_analysis", christological_analysis,
        category="christological", description="Christ-centered content detection",
        tags=["christ", "messiah", "incarnation"]
    )
    framework.register_algorithm(
        "cross_reference_detection", cross_reference_detection,
        category="cross_reference", description="Inter-textual connection detection",
        tags=["connections", "references", "intertextuality"]
    )
    framework.register_algorithm(
        "literary_analysis", literary_analysis,
        category="literary", description="Poetic and rhetorical device analysis",
        tags=["poetry", "rhetoric", "devices"]
    )
    framework.register_algorithm(
        "ethical_analysis", ethical_analysis,
        category="ethical", description="Moral and prescriptive content analysis",
        tags=["ethics", "morality", "prescription"]
    )
    framework.register_algorithm(
        "temporal_analysis", temporal_analysis,
        category="temporal", description="Time-based pattern analysis",
        tags=["time", "tense", "sequence"]
    )
    framework.register_algorithm(
        "eschatological_analysis", eschatological_analysis,
        category="eschatological", description="End-times theme detection",
        tags=["eschatology", "prophecy", "end-times"]
    )
    framework.register_algorithm(
        "historical_analysis", historical_analysis,
        category="historical", description="Historical context analysis",
        tags=["history", "culture", "context"]
    )

    # Create sample passage (metadata auto-populated)
    sample_passage = BiblicalPassage(
        reference="John 1:1",
        text="In the beginning was the Word, and the Word was with God, and the Word was God.",
        version="ESV",
        testament="New",
        book="John",
        chapter=1,
        verse=1,
        themes=["creation", "divine nature"],
        cross_references=["Genesis 1:1", "Colossians 1:15"]
    )

    print(f"Passage metadata: word_count={sample_passage.word_count}, keywords={sample_passage.keywords}")

    # BibleLoader demonstration (v0.0.8)
    print(f"\nBibleLoader System (v0.0.8):")
    loader = BibleLoader()

    # For demo, create a small sample corpus
    sample_corpus = [
        BiblicalPassage(reference="Genesis 1:1", text="In the beginning God created the heaven and the earth.", testament="Old", book="Genesis", chapter=1, verse=1),
        BiblicalPassage(reference="John 1:1", text="In the beginning was the Word, and the Word was with God, and the Word was God.", testament="New", book="John", chapter=1, verse=1),
        BiblicalPassage(reference="Proverbs 8:22", text="The LORD possessed me in the beginning of his way, before his works of old.", testament="Old", book="Proverbs", chapter=8, verse=22),
    ]

    loader.passages = sample_corpus
    loader._organize_by_book()

    corpus_stats = loader.get_statistics()
    print(f"Sample corpus loaded: {corpus_stats['total_passages']} passages, {corpus_stats['total_books']} books")
    print(f"Corpus statistics: {corpus_stats['total_words']} words, {corpus_stats['unique_words']} unique words")

    # Plugin system demonstration (v0.0.6)
    print(f"\nPlugin System (v0.0.6):")
    print(f"  Total plugins registered: {len(framework.plugins)}")
    print(f"  Categories: {framework.get_plugin_categories()}")
    for category in framework.get_plugin_categories():
        plugins_in_cat = framework.list_plugins(category)
        print(f"  {category.title()}: {len(plugins_in_cat)} plugins")

    # Multi-dimensional analysis (v0.0.4)
    analyzer = MultiDimensionalAnalyzer(framework)
    multi_result = analyzer.analyze(sample_passage)

    print(f"\nMulti-dimensional analysis:")
    print(f"  Dimensions analyzed: {len(multi_result.dimension_results)}")
    print(f"  Total insights: {multi_result.get_total_insights()}")
    print(f"  Total findings: {multi_result.get_total_findings()}")
    print(f"  Average confidence: {multi_result.get_average_confidence():.2f}")
    print(f"  Multiplication factor: {multi_result.multiplication_factor}x")

    print(f"\nSynthesis: {multi_result.synthesis}")

    # Dimension interaction analysis
    interaction_analyzer = DimensionInteractionAnalyzer()
    interactions = interaction_analyzer.analyze_interactions(multi_result.dimension_results)

    print(f"\nDimension Interactions:")
    print(f"  Resonance Score: {interactions['resonance_score']:.2f}")
    print(f"  Reinforcements: {len(interactions['reinforcements'])}")
    print(f"  Tensions: {len(interactions['tensions'])}")
    print(f"  Emergent Patterns: {len(interactions['emergent_patterns'])}")
    print(f"  Semantic Interactions: {len(interactions['semantic_interactions'])}")
    print(f"  Theological Framework: {interactions['theological_synthesis']['dominant_theological_framework']}")

    # Validation (v0.0.6 rule-based)
    validator = ValidationEngine()
    validation = validator.validate_analysis(multi_result)

    print(f"\nValidation Results (Rule-based v0.0.6):")
    print(f"  Rules Evaluated: {validation['rules_evaluated']}")
    print(f"  Validation Passed: {validation['validation_passed']}")
    print(f"  Issues Found: {validation['issues_found']}")
    if validation['issues']:
        for issue in validation['issues'][:2]:  # Show first 2 issues
            print(f"  - {issue['rule_name']}: {issue['description']} (severity: {issue['severity']})")

    # Sower metrics
    sower_metrics = SowerMetrics()
    metrics = sower_metrics.compute_metrics([multi_result])
    classification = sower_metrics.get_sower_classification(metrics['growth_index'])

    print(f"\nSower Metrics (Matthew 13:8):")
    print(f"  Interpretive Yield: {metrics['interpretive_yield']}")
    print(f"  Average Fold: {metrics['average_fold']}")
    print(f"  Growth Index: {metrics['growth_index']}")
    print(f"  Classification: {classification}")

    # Show results by dimension (sample of key dimensions)
    key_dimensions = [AnalysisDimension.LEXICAL, AnalysisDimension.THEMATIC,
                     AnalysisDimension.TEMPORAL, AnalysisDimension.ESCHATOLOGICAL,
                     AnalysisDimension.HISTORICAL]

    for dimension in key_dimensions:
        if dimension in multi_result.dimension_results:
            result = multi_result.dimension_results[dimension]
            print(f"\n{dimension.value.upper()} ANALYSIS:")
            print(f"  Findings: {result.findings}")
            print(f"  Insights: {result.insights}")
            print(f"  Confidence: {result.confidence}")

    # Export multi-dimensional results
    framework.export_multidimensional_results([multi_result], "baseline_multidimensional_results.json")
    framework.export_multidimensional_markdown([multi_result], "baseline_multidimensional_report.md")
    framework.export_interactive_html([multi_result], "baseline_analysis_report.html")
    print(f"\nMulti-dimensional results exported to baseline_multidimensional_results.json, baseline_multidimensional_report.md, and baseline_analysis_report.html (v{__version__})")

    # v0.0.9 Features Demonstration
    print(f"\n=== v0.0.9 Features Demonstration ===")

    # Genre Detection
    print(f"\nGenreDetector (v0.0.9):")
    genre_detector = GenreDetector()
    genre_classification = genre_detector.classify_genre(sample_passage)
    print(f"  Primary Genre: {genre_classification.primary_genre}")
    print(f"  Secondary Genres: {genre_classification.secondary_genres}")
    print(f"  Confidence: {genre_classification.confidence_scores[genre_classification.primary_genre]:.2f}")

    # Theological Ontology
    print(f"\nTheologicalOntology (v0.0.9):")
    ontology = TheologicalOntology()
    concept_mappings = ontology.map_passage_to_concepts(sample_passage)
    print(f"  Concepts Mapped: {len(concept_mappings)}")
    if concept_mappings:
        top_concept = concept_mappings[0]
        print(f"  Top Concept: {top_concept.concept_name} (strength: {top_concept.strength:.2f})")
        theological_depth = ontology.get_theological_depth(concept_mappings)
        print(f"  Theological Depth Score: {theological_depth['depth_score']:.2f}")

    # Batch Analysis
    print(f"\nBatchAnalyzer (v0.0.9):")
    batch_analyzer = BatchAnalyzer(framework)
    batch_result = batch_analyzer.analyze_batch(sample_corpus)
    print(f"  Batch Analysis: {batch_result.passages_analyzed} passages in {batch_result.processing_time:.2f}s")
    print(f"  Average Confidence: {batch_result.average_confidence:.2f}")
    print(f"  Total Insights: {batch_result.total_insights}")

    # Export batch results
    batch_analyzer.export_batch_results(batch_result, "baseline_batch_results.json")
    print(f"  Batch results exported to baseline_batch_results.json")

    print(f"\nSUCCESS: Bible Algorithmic Project v{__version__} - All features successfully demonstrated!")