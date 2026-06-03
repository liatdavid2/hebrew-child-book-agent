# Hebrew Children's Book Generator

A full-stack AI project for generating personalized Hebrew children's books.

The system includes a Hebrew user interface, a FastAPI backend, a LangGraph-based generation workflow, and OpenAI models for text and image generation.

## What the project does

The application receives user input in Hebrew, including:

- Cover text
- Number of pages
- Hebrew instructions for GPT
- Story style, topic, characters, and additional creative guidance

Based on this input, the system automatically generates a complete Hebrew children's book.

## Main features

- Generates a Hebrew children's story
- Creates a cover image
- Creates a unique image for each page
- Builds an interactive flipping HTML book
- Exports the final result as a ZIP file
- The ZIP is ready to upload directly to GitHub Pages

## Tech stack

- Hebrew UI
- FastAPI backend
- LangGraph workflow
- OpenAI API
- HTML, CSS, and JavaScript
- ZIP export for static hosting

## Generation flow

1. The user enters the book instructions in Hebrew.
2. The backend sends the request to a LangGraph workflow.
3. The workflow generates the story structure and page content.
4. OpenAI is used to generate the Hebrew text and images.
5. The system creates an HTML flipping book.
6. All generated files are packaged into a ZIP.
7. The ZIP can be deployed as a static website using GitHub Pages.

## Output

Each generated book includes:

- `index.html`
- CSS and JavaScript files
- Cover image
- Page images
- Hebrew story content
- Static assets required for GitHub Pages

## GitHub Pages usage

After generating the ZIP file:

1. Extract the ZIP.
2. Upload the extracted files to a GitHub repository.
3. Enable GitHub Pages in the repository settings.
4. Open the generated GitHub Pages URL to view the book online.

## Example use case

A parent can enter a short idea in Hebrew, such as a story about a unicorn, a birthday party, or best friends at the beach.  
The system turns the idea into a complete illustrated Hebrew children's book that can be shared online.
