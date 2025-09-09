# Files Translator Service

This Flask application translates English text to Romanian line by line using an AI model through Ollama.

## Configuration

The application uses the following environment variables:

- `INPUT_FILE_PATH`: Path to the input file containing English text (default: `/app/data/english_text.txt`)
- `OUTPUT_FILE_PATH`: Path to the output file for Romanian translations (default: `/app/data/romanian_text.txt`)
- `OLLAMA_SERVICE_URL`: URL of the Ollama service (default: `http://dockerhost:11434`)
- `ENHANCE_PRODUCT_MODEL`: AI model to use for translation (default: `aya:8b-23`)
- `OLLAMA_API_SERVICE_ENV`: Flask environment (default: `development`)
- `OLLAMA_API_SERVICE_DEBUG`: Flask debug mode (default: `true`)

## API Endpoints

### 1. Process Single Line: `GET /trigger-processing`

Processes the next line from the input file:

- Reads the first line from the input file
- Translates it from English to Romanian using AI
- Appends the translation to the output file
- Removes the processed line from the input file

**Response:**

```json
{
  "status": "success",
  "input": "Hello, how are you today?",
  "output": "Salut, cum ești astăzi?",
  "input_file_path": "/app/data/english_text.txt",
  "output_file_path": "/app/data/romanian_text.txt"
}
```

### 2. Check Status: `GET /status`

Returns the current status of the translation process:

**Response:**

```json
{
  "input_file_path": "/app/data/english_text.txt",
  "output_file_path": "/app/data/romanian_text.txt",
  "input_file_exists": true,
  "output_file_exists": true,
  "lines_remaining": 5,
  "lines_translated": 3
}
```

### 3. Process All Lines: `POST /process-all`

Processes all remaining lines in the input file in one request:

**Response:**

```json
{
  "status": "completed",
  "processed_count": 5,
  "skipped_count": 0,
  "errors": [],
  "input_file_path": "/app/data/english_text.txt",
  "output_file_path": "/app/data/romanian_text.txt"
}
```

## Usage

1. Place your English text file at the configured input path (one line per sentence/phrase)
2. Call the API endpoints to start translation. Or for a smoother experience, just visit the home route (`/`) for a basic UI interface that facilitates the project controls
3. The translated text will be saved to the output file
4. Each processed line is removed from the input file to facilitate some sort of durable execution

## Example Docker Environment Variables

```bash
INPUT_FILE_PATH=/app/data/english_input.txt
OUTPUT_FILE_PATH=/app/data/romanian_output.txt
OLLAMA_SERVICE_URL=http://ollama:11434
ENHANCE_PRODUCT_MODEL=aya:8b-23
```

> (!) The `/app/data` represents the path inside the docker container. It is mapped to `services/files-translator-service` directly so just place the files there for usage.
