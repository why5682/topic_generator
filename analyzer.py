import ollama
from pydantic import BaseModel, Field
from typing import List

class Hypothesis(BaseModel):
    title: str = Field(description="Proposed research title")
    rationale: str = Field(description="Why this is important based on the gaps")
    methodology: str = Field(description="Suggested study design")

class TrendAnalysisResult(BaseModel):
    trend_summary: str = Field(description="Summary of current research trends")
    identified_gaps: List[str] = Field(description="List of missed areas")
    hypotheses: List[Hypothesis] = Field(description="3 specific research proposals")

class TrendAnalyzer:
    def __init__(self, model_name: str, ollama_client=None): 
        self.model_name = model_name
        self.client = ollama_client  # Use provided client or default to ollama module

    def analyze_and_hypothesize(self, abstracts: List[dict], topic: str) -> TrendAnalysisResult:
        if not abstracts:
            return TrendAnalysisResult(trend_summary="No data.", identified_gaps=[], hypotheses=[])

        context_text = ""
        for i, paper in enumerate(abstracts):
            context_text += f"[{i+1}] Title: {paper['title']}\nAbstract: {paper['abstract']}\n\n"

        prompt = f"""
        You are a senior Pharmacoepidemiologist specializing in Real-World Evidence (RWE) using administrative claims/EHR databases. 
        
        Analyze the provided abstracts related to '{topic}'.
        
        **CRITICAL INSTRUCTION: NOVELTY CHECK**
        - Do NOT propose hypotheses that are already the main subject of the provided abstracts.
        - You must propose **NOVEL** research questions that address UNANSWERED gaps.
        
        1. **Summarize Key Research Trends**: Briefly outline what is currently being studied.
        2. **Identify Specific Evidence Gaps**: 
           - Focus on areas where observational data is needed but missing.
           - Look for: Missing head-to-head comparisons, unstudied high-risk subgroups (e.g., elderly, CKD), or long-term safety signals not feasible in RCTs.
           - do NOT leave this empty. If explicit gaps aren't stated, infer them from what is *absent* in the trends.
        3. **Propose 3 NOVEL Research Hypotheses**:
           - **Design**: Retrospective Cohort Study (New-User Active Comparator Design).
           - **Data Source**: Claims data or EHR.
           - **Structure**:
             - **Title**: Specific and professional.
             - **Rationale**: Why this is needed now? (Cite specific conflicting or missing evidence).
             - **Methodology**: Be highly specific. Mention:
               * Study Population (Inclusion/Exclusion)
               * Comparator Drug (Active comparator)
               * Primary Outcome (Specific ICD/procedure codes concept)
               * Statistical Approach (e.g., Propensity Score Matching/Weighting, HDPS).

        **REQUIRED JSON OUTPUT FORMAT**:
        {{
            "trend_summary": "Summary text...",
            "identified_gaps": ["Gap 1", "Gap 2", "Gap 3"],
            "hypotheses": [
                {{
                    "title": "Hypothesis Title",
                    "rationale": "Why needed...",
                    "methodology": "Study Design..."
                }}
            ]
        }}
        
        Use Chain of Thought, but ensure the FINAL output is strictly valid JSON matching the above keys. 
        Do not include any conversational text outside the JSON.
        
        Abstracts: {context_text}
        """
        
        try:
            print(f"DEBUG: Sending request to Ollama ({self.model_name})...")
            
            # Use provided client or fallback to ollama module
            chat_func = self.client.chat if self.client else ollama.chat
            
            response = chat_func(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json', 
                options={'temperature': 0.7}
            )
            
            content = response['message']['content']
            print("DEBUG: Raw LLM Output start ---")
            print(content)
            print("DEBUG: Raw LLM Output end ---")
            
            # Sanitization: Remove Markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Attempt to parse JSON strictly first
            import json
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                raise ValueError(f"LLM did not return valid JSON. Content: {content[:100]}...")

            # --- Robust Normalization ---
            print("DEBUG: Running Robust Normalization Logic...")
            normalized_data = {}
            
            # Helper to find value by flexible keys
            def find_value(targets: List[str], source: dict):
                # Flatten keys: lowercase, remove _ and spaces
                source_map = {k.lower().replace("_", "").replace(" ", ""): v for k, v in source.items()}
                
                for target in targets:
                    target_clean = target.lower().replace("_", "")
                    if target_clean in source_map:
                        return source_map[target_clean]
                return None

            # 1. Trend Summary (Target: str)
            val = find_value(["trend_summary", "key_research_trends", "trends", "summary", "current_trends"], data)
            if val:
                if isinstance(val, list):
                    # If it's a list of strings or dicts, join them
                    normalized_data["trend_summary"] = "\n".join([str(x) for x in val])
                else:
                    normalized_data["trend_summary"] = str(val)
            else:
                normalized_data["trend_summary"] = "Trend summary was not generated by the model."

            # 2. Identified Gaps (Target: List[str])
            val = find_value(["identified_gaps", "gaps", "evidence_gaps", "missing_evidence", "gaps_in_evidence"], data)
            if val:
                if isinstance(val, str):
                    normalized_data["identified_gaps"] = [val]
                elif isinstance(val, list):
                    normalized_data["identified_gaps"] = [str(v) for v in val]
                else:
                    normalized_data["identified_gaps"] = ["Model returned empty gaps."]
            else:
                normalized_data["identified_gaps"] = ["No specific gaps were generated by the model."]

            # Helper to force string format from complex types
            def ensure_string(val):
                if val is None: return "N/A"
                if isinstance(val, str): return val
                if isinstance(val, (int, float)): return str(val)
                if isinstance(val, dict):
                    # If it's a dict (e.g. {'design': '...'}, just join the values)
                    return ". ".join([str(v) for v in val.values() if isinstance(v, (str, int, float))])
                if isinstance(val, list):
                    return ". ".join([str(v) for v in val])
                return str(val)

            # 3. Hypotheses (Target: List[Hypothesis])
            val = find_value(["hypotheses", "proposed_hypotheses", "research_hypotheses", "new_hypotheses"], data)
            if val and isinstance(val, list):
                clean_hypotheses = []
                for item in val:
                    # Normalize item keys too (Title, Rationale, Methodology)
                    if isinstance(item, dict):
                        h_title = find_value(["title", "hypothesis", "topic"], item)
                        h_rationale = find_value(["rationale", "reasoning", "justification", "background"], item)
                        h_method = find_value(["methodology", "method", "study_design", "design", "approach"], item)
                        
                        clean_hypotheses.append({
                            "title": ensure_string(h_title) or "Untitled Hypothesis",
                            "rationale": ensure_string(h_rationale) or "Rationale missing.",
                            "methodology": ensure_string(h_method) or "Methodology missing."
                        })
                normalized_data["hypotheses"] = clean_hypotheses
            else:
                normalized_data["hypotheses"] = [{
                    "title": "Hypothesis Generation Failed", 
                    "rationale": "The model failed to produce structured hypotheses.", 
                    "methodology": "Please try again."
                }]

            # Re-serialize for Pydantic validation
            return TrendAnalysisResult.model_validate(normalized_data)
        except Exception as e:
            return TrendAnalysisResult(
                trend_summary=f"Analysis failed: {str(e)}",
                identified_gaps=[],
                hypotheses=[]
            )
