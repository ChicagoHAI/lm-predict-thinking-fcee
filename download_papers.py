import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import time

def search_arxiv(query, max_results=1):
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = urllib.parse.quote(query)
    url = f'{base_url}search_query=all:{search_query}&start=0&max_results={max_results}'
    
    try:
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        return data
    except Exception as e:
        print(f"Error searching arXiv: {e}")
        return None

def download_paper(entry, save_dir):
    try:
        id_url = entry.find('{http://www.w3.org/2005/Atom}id').text
        arxiv_id = id_url.split('/')[-1]
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.replace('\n', ' ').strip()
        # Sanitize title
        safe_title = "".join([c if c.isalnum() or c in [' ', '-', '_'] else "" for c in title])[:100]
        safe_title = safe_title.replace(' ', '_')
        
        pdf_link = None
        for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
            if link.attrib.get('title') == 'pdf':
                pdf_link = link.attrib['href']
                break
        
        if not pdf_link:
            # Fallback: construct PDF link from ID
            pdf_link = f'http://arxiv.org/pdf/{arxiv_id}.pdf'
            
        filename = f"{arxiv_id}_{safe_title}.pdf"
        filepath = os.path.join(save_dir, filename)
        
        print(f"Downloading: {title}...")
        urllib.request.urlretrieve(pdf_link, filepath)
        print(f"Saved to {filepath}")
        return {
            'title': title,
            'filename': filename,
            'id': arxiv_id,
            'authors': [a.find('{http://www.w3.org/2005/Atom}name').text for a in entry.findall('{http://www.w3.org/2005/Atom}author')],
            'summary': entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
        }
    except Exception as e:
        print(f"Error downloading {title}: {e}")
        return None

def main():
    papers_dir = 'papers'
    if not os.path.exists(papers_dir):
        os.makedirs(papers_dir)
        
    queries = [
        "Response Length Perception and Sequence Scheduling",
        "CASTILLO Characterizing Response Length Distributions",
        "ForeLen Forecasting the Length of LLM Responses",
        "LLM inference latency prediction" 
    ]
    
    downloaded_papers = []
    
    for q in queries:
        print(f"Searching for: {q}")
        xml_data = search_arxiv(q)
        if xml_data:
            root = ET.fromstring(xml_data)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            if entries:
                paper_info = download_paper(entries[0], papers_dir)
                if paper_info:
                    downloaded_papers.append(paper_info)
            else:
                print(f"No results found for: {q}")
        time.sleep(3) # Be nice to API

    # Generate README
    with open(os.path.join(papers_dir, 'README.md'), 'w') as f:
        f.write("# Downloaded Papers\n\n")
        for p in downloaded_papers:
            f.write(f"## [{p['title']}]({p['filename']})\n")
            f.write(f"- **Authors**: {', '.join(p['authors'][:3])} et al.\n")
            f.write(f"- **arXiv ID**: {p['id']}\n")
            f.write(f"- **Summary**: {p['summary'][:200]}...\n\n")

if __name__ == "__main__":
    main()
