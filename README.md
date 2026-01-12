# DocuStream Pro - Advanced Document Consolidation Platform

![DocuStream Pro](https://img.shields.io/badge/DocuStream%20Pro-Document%20Merger-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**DocuStream Pro** is a powerful, web-based document consolidation platform that enables seamless merging of multiple files from various sources into unified output formats. Built with Streamlit, it provides an intuitive interface for developers, writers, and teams to combine code files, documents, and text content efficiently.

## 🚀 Key Features

### 📥 Multiple Import Sources
- **File Upload**: Drag & drop multiple files directly
- **Paste Content**: Quick text/code pasting with custom filenames
- **GitHub Integration**: 
  - Single file URLs
  - GitHub Gist import
  - Full repository explorer with tree selection
- **Smart Filtering**: Exclude common directories, filter by extensions

### 🎯 Advanced Processing
- **Content Sanitization**: 
  - Automatic API key redaction (OpenAI, AWS, Google)
  - Optional comment removal (Python/JS style)
- **Deduplication**: SHA-256 hashing prevents duplicate content
- **Token Counting**: Real-time token count for AI model context limits
  - Supports: GPT-4o, GPT-4 Turbo, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.3 70B

### 📄 Flexible Output Formats
- **TXT**: Plain text with smart markdown formatting
- **PDF**: Professional PDF documents
- **DOCX**: Microsoft Word documents

### 🛡️ Security & Validation
- Rate limiting for API calls (60 req/hour default)
- Filename validation and sanitization
- Path traversal protection
- URL validation (GitHub domains only)

## 🏗️ Project Structure

```
File Merger WebApp/
├── app.py                      # Main Streamlit application
├── processor.py                # Core document processing logic
├── github_api.py               # GitHub API integration
├── utils.py                    # Utility functions & helpers
├── test_processor.py           # Unit tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Docker Compose setup
├── .dockerignore               # Docker ignore patterns
└── .gitignore                  # Git ignore patterns
```

## 📋 Requirements

- Python 3.11+
- LibreOffice (for PDF conversion from non-PDF formats)
- Streamlit-compatible browser

## 🔧 Installation

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Noob-Coder2/DocuMerger
   cd "DocuMerger"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install LibreOffice** (for PDF conversion):
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install libreoffice default-jre
   ```
   
   **macOS:**
   ```bash
   brew install --cask libreoffice
   ```
   
   **Windows:**
   - Download from [LibreOffice website](https://www.libreoffice.org/)
   - Ensure it's added to system PATH

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

2. **Or build manually:**
   ```bash
   docker build -t docustream-pro .
   docker run -p 8501:8501 docustream-pro
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

## 🎯 Usage Guide

### 1. Import Files

#### Upload Files
- Navigate to the **"📂 Upload Files"** tab
- Drag & drop or click to select multiple files
- Files are automatically added to the queue

#### Paste Content
- Go to the **"📝 Paste/Gist"** tab
- Enter a filename and paste your content
- Click **"➕ Add to Queue"**
- Or import from GitHub Gist by providing the Gist URL

#### GitHub Import
- **Single File**: Paste a GitHub file URL (e.g., `https://github.com/user/repo/blob/main/file.py`)
- **Repository Explorer**: 
  1. Enter repository URL
  2. (Optional) Add GitHub token for private repos or rate limits
  3. Apply filters (exclude common dirs, source-only mode)
  4. Click **"🔍 Load Repository"**
  5. Select files from the tree view
  6. Click **"📥 Import Selected Files"**

### 2. Organize Files

- **Search**: Filter files by name
- **Preview**: Click 👁️ to preview file content
- **Remove**: Click ❌ to remove files from queue
- **Reorder**: Drag files to change processing order
- **Clear All**: Remove all files from queue

### 3. Configure Output

- **Output Format**: Select TXT, PDF, or DOCX
- **Output Filename**: Enter base name (extension added automatically)
- **Sanitization Options**:
  - **Strip API Keys**: Removes common API key patterns
  - **Remove Comments**: Removes Python/JS style comments

### 4. Merge Documents

- Click **"🚀 Merge Documents"**
- Wait for processing to complete
- Download the consolidated file using the download button

## 🔧 Configuration

### Model Context Limits

The application tracks token usage against popular AI model limits:

| Model | Context Limit | Icon |
|-------|---------------|------|
| GPT-4o | 128,000 tokens | 🟢 |
| GPT-4 Turbo | 128,000 tokens | 🔵 |
| Claude 3.5 Sonnet | 200,000 tokens | 🟠 |
| Gemini 1.5 Pro | 1,000,000 tokens | 🔴 |
| Llama 3.3 70B | 128,000 tokens | 🟣 |

### Rate Limiting

- **Default**: 60 API calls per hour
- **GitHub API**: Without token, limited to 60 req/hour
- **With Token**: Higher limits for authenticated requests

### Filter Presets

#### Exclude Common Dirs
Automatically excludes:
- `node_modules`, `venv`, `.venv`, `env`, `.env`
- `__pycache__`, `.git`, `.svn`, `.hg`
- `dist`, `build`, `.next`, `.nuxt`
- `coverage`, `.nyc_output`, `.pytest_cache`
- `vendor`, `packages`, `.idea`, `.vscode`

#### Source Files Only
Includes only code files:
- `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`
- `.c`, `.cpp`, `.h`, `.cs`, `.go`, `.rs`
- `.rb`, `.php`, `.swift`, `.kt`, `.scala`
- `.vue`, `.svelte`, `.html`, `.css`, `.scss`, `.sass`, `.less`

## 📊 Processing Lanes

### Text Lane (TXT Output)
- **Fast**: Instant text merging
- **Smart**: Automatic markdown formatting for code files
- **Flexible**: Handles any text-based content

### Fast Lane (PDF Merge)
- **Requirements**: All input files must be PDFs
- **Process**: Direct PDF merging using PyPDF
- **Speed**: Very fast, no conversion needed

### Heavy Lane (PDF Conversion)
- **Requirements**: LibreOffice installed
- **Process**: Converts non-PDF files → PDF → Merge
- **Supported**: DOCX, TXT, and other LibreOffice-compatible formats

### Word Lane (DOCX Merge)
- **Requirements**: All input files must be DOCX
- **Process**: Merges Word documents preserving styles
- **Note**: Other formats must be converted externally first

## 🔒 Security Features

### Input Validation
- Filename validation (length, path traversal, invalid characters)
- URL validation (GitHub domains only)
- File size limits (configurable)

### Content Sanitization
- **API Key Patterns**:
  - OpenAI: `sk-` followed by 20+ alphanumeric
  - AWS: `AKIA` followed by 16 uppercase alphanumeric
  - Google: `AIza` followed by 35+ characters
  - Generic: `api_key=`, `apikey=`, `api-key=` patterns

- **Comment Removal** (heuristic):
  - Preserves URLs and strings
  - Removes `#` and `//` style comments
  - May have edge cases with complex strings

### Rate Limiting
- Prevents API abuse
- Tracks calls per time window
- Provides reset time estimates

## 🧪 Testing

Run unit tests for the processor module:

```bash
python test_processor.py
```

Tests cover:
- Token counting functionality
- Text merging logic
- File handling

## 🐛 Troubleshooting

### Common Issues

**LibreOffice not found**
```bash
# Verify installation
soffice --version

# Add to PATH if needed
export PATH="/path/to/libreoffice/program:$PATH"
```

**GitHub API Rate Limit**
- Add a Personal Access Token in the "Advanced" section
- Token needs `repo` scope for private repos

**PDF Conversion Fails**
- Ensure LibreOffice is installed and accessible
- Check file permissions in temp directory
- Verify file format is supported

**Large Repository Loading**
- Use filters to reduce file count
- Consider loading specific folders only
- Add GitHub token to avoid rate limits

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_processor.py

# Run application
streamlit run app.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web app framework
- **PyPDF**: For PDF processing capabilities
- **python-docx**: For Word document handling
- **docxcompose**: For DOCX merging functionality
- **tiktoken**: For accurate token counting
- **GitHub API**: For repository integration

## 📞 Support

For issues, questions, or contributions:
1. Check the [Issues](https://github.com/Noob-Coder2/DocuMerger/issues) page
2. Review this README and documentation
3. Open a new issue with detailed information

---

**Built with ❤️ for developers, by developers**