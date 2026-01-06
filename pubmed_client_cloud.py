import os
import sqlite3
import json
import time
import ssl
import streamlit as st
from typing import List, Dict, Optional
from Bio import Entrez

# --- SSL FIX: Bypass SSL Verification ---
# This fixes "CERTIFICATE_VERIFY_FAILED" errors
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
# -----------------------------------------

class PubMedClient:
    def __init__(self, db_path: str = "pubmed_cache.db"):
        # Try to get from Streamlit secrets first, fallback to environment variables
        try:
            self.email = st.secrets.get("ENTREZ_EMAIL", os.getenv("ENTREZ_EMAIL"))
            self.api_key = st.secrets.get("ENTREZ_API_KEY", os.getenv("ENTREZ_API_KEY"))
        except Exception:
            self.email = os.getenv("ENTREZ_EMAIL")
            self.api_key = os.getenv("ENTREZ_API_KEY")
        
        # Fallback if email is missing (NCBI requires an email)
        if not self.email:
            print("Warning: ENTREZ_EMAIL not found. Using default.")
            self.email = "tool_user@example.com"
        
        Entrez.email = self.email
        if self.api_key:
            Entrez.api_key = self.api_key
            
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS searches (
                    query TEXT PRIMARY KEY,
                    results TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()

    def _get_from_cache(self, query: str) -> Optional[List[Dict]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT results FROM searches WHERE query = ?", (query,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return None
        return None

    def _save_to_cache(self, query: str, results: List[Dict]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO searches (query, results, timestamp) VALUES (?, ?, ?)",
                (query, json.dumps(results), time.time())
            )
            conn.commit()

    def fetch_abstracts(self, query: str, max_results: int = 20) -> List[Dict]:
        cache_key = f"{query}::{max_results}"
        
        # 1. Check Cache
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            print(f"DEBUG: Cache hit for '{query}'")
            return cached_data

        print(f"DEBUG: Fetching live data from PubMed for '{query}'...")
        
        try:
            # 2. Search for IDs
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
            record = Entrez.read(handle)
            handle.close()
            
            id_list = record["IdList"]
            print(f"DEBUG: Found {len(id_list)} IDs: {id_list}")
            
            if not id_list:
                return []

            # 3. Fetch details
            handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
            papers = Entrez.read(handle)
            handle.close()

            results = []
            if 'PubmedArticle' in papers:
                for article in papers['PubmedArticle']:
                    try:
                        medline = article['MedlineCitation']
                        article_data = article['PubmedData']
                        
                        title = medline['Article']['ArticleTitle']
                        
                        abstract_text = ""
                        if 'Abstract' in medline['Article']:
                            ab = medline['Article']['Abstract']['AbstractText']
                            if isinstance(ab, list):
                                abstract_text = " ".join(ab)
                            else:
                                abstract_text = str(ab)
                        
                        authors = []
                        if 'AuthorList' in medline['Article']:
                            for author in medline['Article']['AuthorList']:
                                if 'LastName' in author and 'ForeName' in author:
                                    authors.append(f"{author['LastName']} {author['ForeName']}")
                        
                        # Handle Date Parsing carefully
                        pub_date = "Unknown"
                        if 'History' in article_data and len(article_data['History']) > 0:
                            if 'Year' in article_data['History'][0]:
                                pub_date = article_data['History'][0]['Year']
                        
                        results.append({
                            "title": title,
                            "abstract": abstract_text,
                            "authors": authors,
                            "date": pub_date,
                            "pmid": medline['PMID']
                        })
                    except Exception as e:
                        print(f"Warning: Failed to parse a specific paper: {e}")
                        continue
            
            print(f"DEBUG: Successfully parsed {len(results)} papers.")
            self._save_to_cache(cache_key, results)
            return results

        except Exception as e:
            print(f"CRITICAL ERROR in fetch_abstracts: {e}")
            import traceback
            traceback.print_exc()
            return []
