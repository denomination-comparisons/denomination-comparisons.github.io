
from app import create_app, socketio
import sys
import asyncio
from app.tools.text_processor import TextProcessor

app = create_app()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'generate-gy25':
        # Batch processing: python run.py generate-gy25 input.txt output.md --book "Book Title" --options cefr=B1
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        book_title = "Unknown"
        options = {}
        for arg in sys.argv[4:]:
            if arg.startswith('--book'):
                book_title = arg.split('=')[1]
            elif arg.startswith('--options'):
                opts = arg.split('=')[1].split(',')
                for opt in opts:
                    if '=' in opt:
                        k, v = opt.split('=')
                        options[k] = v
                    else:
                        options[opt] = True
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        processor = TextProcessor()
        result = asyncio.run(processor.process_book_guide(text, 'text', book_title, options))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.get('modified_text', result.get('original_text', '')))
        print(f"Processed and saved to {output_file}")
    else:
        socketio.run(app, debug=True)
