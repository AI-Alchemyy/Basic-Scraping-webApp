from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from docx import Document
import io
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    action = data.get('action')  # Get the action from the frontend
    
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all paragraph text
        paragraphs = soup.find_all('p')
        content = ' '.join([p.text for p in paragraphs])
        
        # Use regular expressions to remove extra spaces and newlines
        cleaned_content = re.sub(r'\s+', ' ', content).strip()
        
        if action == 'download':
            # Create a .docx file with the scraped content
            doc = Document()
            doc.add_paragraph(cleaned_content)
            doc_io = io.BytesIO()  # Create an in-memory bytes buffer
            doc.save(doc_io)
            doc_io.seek(0)  # Go to the beginning of the buffer
            
            # Send the file as a response with the specified filename
            return send_file(
                doc_io, 
                as_attachment=True, 
                download_name='scraped_content.docx', 
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            return jsonify({'content': cleaned_content})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/sitemap-extract', methods=['POST'])
def sitemap_extract():
    data = request.get_json()
    sitemap_url = data.get('sitemap_url')

    if not sitemap_url:
        return jsonify({'error': 'Missing sitemap URL'}), 400

    try:
        response = requests.get(sitemap_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = [url.text for url in soup.find_all('loc')]
        
        # Filter out non-HTTP/HTTPS URLs
        urls = [url for url in urls if urlparse(url).scheme in ('http', 'https')]
        
        return jsonify({'urls': urls})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
