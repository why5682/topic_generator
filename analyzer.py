import ollama
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json


# ========================================
# Pydantic Models for TTE-based Analysis
# ========================================

class TargetTrialComponents(BaseModel):
    """Target Trial Emulation components"""
    population: str = Field(description="Code-able eligibility criteria")
    intervention: str = Field(description="Index drug definition")
    comparator: str = Field(description="Active comparator with clinical equipoise justification")
    outcome_operational_def: str = Field(description="Specific outcome definition (e.g., Inpatient + ICD)")
    follow_up: str = Field(description="Start/End/Censoring events definition")
    time_zero_definition: Optional[str] = Field(default="Date of first prescription", description="Index date definition")


class BiasMitigation(BaseModel):
    """Bias mitigation strategies"""
    key_confounders: List[str] = Field(description="List of key confounders for PS adjustment")
    negative_control_outcome: str = Field(description="Suggested falsification outcome")
    sensitivity_analysis: Optional[str] = Field(default=None, description="E-value or QBA approach")


class FeasibilityAssessment(BaseModel):
    """Feasibility assessment for RWD study"""
    data_source_suitability: str = Field(description="Why Claims/EMR fits this study")
    potential_challenges: str = Field(description="Key challenges and limitations")
    expected_sample_size: Optional[str] = Field(default="Medium", description="Low/Medium/High estimate")


class Hypothesis(BaseModel):
    """Research hypothesis with TTE framework"""
    title: str = Field(description="Publication-ready academic title")
    research_question: str = Field(description="PICO format research question")
    rationale: str = Field(description="Why this study is needed now")
    study_design: str = Field(default="Active Comparator New User Design", description="Study design")
    target_trial_components: TargetTrialComponents = Field(description="TTE framework components")
    bias_mitigation: BiasMitigation = Field(description="Bias control strategies")
    feasibility_assessment: FeasibilityAssessment = Field(description="RWD feasibility")


class IdentifiedGap(BaseModel):
    """Evidence gap with feasibility status"""
    gap: str = Field(description="Specific description of evidence gap")
    category: Optional[str] = Field(default="General", description="Comparator/Population/Outcome/Temporal")
    feasibility_status: str = Field(description="High/Medium/Low with reason")


class TrendAnalysisResult(BaseModel):
    """Complete TTE-based trend analysis result"""
    landscape_summary: str = Field(description="Overview of current research landscape")
    identified_gaps: List[IdentifiedGap] = Field(description="List of feasible evidence gaps")
    hypotheses: List[Hypothesis] = Field(description="TTE-based research proposals")


class TrendAnalyzer:
    def __init__(self, model_name: str, ollama_client=None): 
        self.model_name = model_name
        self.client = ollama_client

    def analyze_and_hypothesize(self, abstracts: List[dict], topic: str, 
                                 prompt_options: dict = None) -> TrendAnalysisResult:
        if not abstracts:
            return TrendAnalysisResult(
                landscape_summary="No data provided.",
                identified_gaps=[],
                hypotheses=[]
            )
        
        # Default options
        options = prompt_options or {
            'num_hypotheses': 3,
            'include_tte': True,
            'include_bias': True,
            'include_feasibility': True,
            'focus_areas': ["Comparator Gaps", "Population Gaps"]
        }

        context_text = ""
        for i, paper in enumerate(abstracts):
            context_text += f"[{i+1}] Title: {paper['title']}\nAbstract: {paper['abstract']}\n\n"
        
        # Build dynamic prompt
        prompt = self._build_prompt(topic, context_text, options)
        
        try:
            print(f"DEBUG: Sending request to Ollama ({self.model_name})...")
            
            chat_func = self.client.chat if self.client else ollama.chat
            
            response = chat_func(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json', 
                options={'temperature': 0.7}
            )
            
            content = response['message']['content']
            print("DEBUG: Raw LLM Output received")
            
            # Sanitize markdown code blocks
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                raise ValueError(f"LLM did not return valid JSON.")

            # Normalize and validate
            normalized_data = self._normalize_response(data, options)
            
            return TrendAnalysisResult.model_validate(normalized_data)
            
        except Exception as e:
            print(f"DEBUG: Analysis error: {e}")
            return TrendAnalysisResult(
                landscape_summary=f"Analysis failed: {str(e)}",
                identified_gaps=[],
                hypotheses=[]
            )
    
    def _build_prompt(self, topic: str, context_text: str, options: dict) -> str:
        """Build dynamic prompt based on user options."""
        
        num_hyp = options.get('num_hypotheses', 3)
        include_tte = options.get('include_tte', True)
        include_bias = options.get('include_bias', True)
        include_feasibility = options.get('include_feasibility', True)
        focus_areas = options.get('focus_areas', ["Comparator Gaps", "Population Gaps"])
        
        # Focus areas text
        focus_text = "\n".join([f"- {area}" for area in focus_areas]) if focus_areas else "- All gap types"
        
        # Base prompt
        prompt = f"""
You are a Principal Pharmacoepidemiologist with expertise in Causal Inference and Target Trial Emulation using administrative claims data (e.g., Medicare, NHIS-HEALS) and EMR.

**TOPIC**: {topic}

**YOUR TASK**: Analyze the provided abstracts to generate scientifically rigorous, RWD-feasible research hypotheses.

---
## STEP 1: LANDSCAPE ANALYSIS
Identify:
- Drug classes/interventions studied.
- Outcomes measured (Distinguish between clinical endpoints vs. surrogate markers).
- Study designs (Note any "Target Trial Emulation" attempts).
- Key limitations mentioned in abstracts.

## STEP 2: GAP & FEASIBILITY IDENTIFICATION
**FOCUS ON THESE GAP TYPES**:
{focus_text}

**CRITICAL FEASIBILITY FILTER**:
- ❌ DISCARD outcomes relying on subjective scores (e.g., pain scale) unless strictly coded.
- ✅ PRIORITIZE outcomes defined by ICD-10, Procedure codes, or Death registries.

## STEP 3: NOVELTY & VALIDITY CHECK
- ⚠️ Check: Is this ALREADY answered?
- ⚠️ Check: Is "New User" design applicable?
- ⚠️ Check: Is there Clinical Equipoise?

## STEP 4: HYPOTHESIS GENERATION
Propose exactly {num_hyp} hypotheses. Focus on "Active Comparator New User Design".
"""
        
        # Add TTE section if enabled
        if include_tte:
            prompt += """
**TTE Components Required**:
- Eligibility Criteria (code-able)
- Treatment Strategies (Index vs Active Comparator)
- Assignment (mimic randomization)
- Follow-up (ITT vs Per-protocol)
- Outcome (operational definition)
- Time Zero (index date)
"""
        
        # Add Bias section if enabled
        if include_bias:
            prompt += """
**Bias Mitigation Required**:
- Key Confounders for PS matching/IPTW
- Negative Control Outcome (falsification test)
- Sensitivity Analysis (E-value or QBA)
"""
        
        # Add Feasibility section if enabled
        if include_feasibility:
            prompt += """
**Feasibility Required**:
- Data source suitability
- Expected sample size (Low/Medium/High)
- Potential challenges
"""
        
        # JSON output format
        prompt += f"""
---
**OUTPUT FORMAT** (Strict JSON):
{{
    "landscape_summary": "Summary text...",
    "identified_gaps": [
        {{
            "gap": "Description",
            "category": "Comparator/Population/Outcome/Temporal",
            "feasibility_status": "High/Medium/Low (Reason)"
        }}
    ],
    "hypotheses": [
        {{
            "title": "Publication-ready title",
            "research_question": "PICO format",
            "rationale": "Why needed",
            "study_design": "Active Comparator New User Design","""
        
        if include_tte:
            prompt += """
            "target_trial_components": {
                "population": "Eligibility criteria",
                "intervention": "Index drug",
                "comparator": "Active comparator",
                "outcome_operational_def": "ICD/procedure codes",
                "follow_up": "Duration/censoring",
                "time_zero_definition": "Index date"
            },"""
        
        if include_bias:
            prompt += """
            "bias_mitigation": {
                "key_confounders": ["List of confounders"],
                "negative_control_outcome": "Falsification outcome",
                "sensitivity_analysis": "E-value approach"
            },"""
        
        if include_feasibility:
            prompt += """
            "feasibility_assessment": {
                "data_source_suitability": "Why fits",
                "potential_challenges": "Limitations",
                "expected_sample_size": "Low/Medium/High"
            }"""
        
        prompt += f"""
        }}
    ]
}}

**ABSTRACTS TO ANALYZE**:
{context_text}

Think step by step. Ensure final output is ONLY valid JSON.
"""
        return prompt

    def _normalize_response(self, data: dict, options: dict) -> dict:
        """Normalize LLM response to match expected structure."""
        
        include_tte = options.get('include_tte', True)
        include_bias = options.get('include_bias', True)
        include_feasibility = options.get('include_feasibility', True)
        
        def find_value(targets: List[str], source: dict):
            if not source:
                return None
            source_map = {k.lower().replace("_", "").replace(" ", ""): v for k, v in source.items()}
            for target in targets:
                target_clean = target.lower().replace("_", "")
                if target_clean in source_map:
                    return source_map[target_clean]
            return None
        
        def ensure_string(val) -> str:
            if val is None: return "N/A"
            if isinstance(val, str): return val
            if isinstance(val, dict): return ". ".join([str(v) for v in val.values() if v])
            if isinstance(val, list): return ". ".join([str(v) for v in val])
            return str(val)
        
        normalized = {}
        
        # 1. Landscape Summary
        val = find_value(["landscape_summary", "trend_summary", "summary"], data)
        normalized["landscape_summary"] = ensure_string(val) or "Landscape summary not generated."
        
        # 2. Identified Gaps
        gaps_val = find_value(["identified_gaps", "gaps", "evidence_gaps"], data)
        normalized["identified_gaps"] = []
        
        if gaps_val and isinstance(gaps_val, list):
            for gap_item in gaps_val:
                if isinstance(gap_item, dict):
                    normalized["identified_gaps"].append({
                        "gap": ensure_string(find_value(["gap", "description"], gap_item)) or "Gap not specified",
                        "category": ensure_string(find_value(["category", "type"], gap_item)) or "General",
                        "feasibility_status": ensure_string(find_value(["feasibility_status", "feasibility"], gap_item)) or "Medium"
                    })
                elif isinstance(gap_item, str):
                    normalized["identified_gaps"].append({
                        "gap": gap_item,
                        "category": "General",
                        "feasibility_status": "Medium"
                    })
        
        if not normalized["identified_gaps"]:
            normalized["identified_gaps"] = [{"gap": "No gaps identified", "category": "General", "feasibility_status": "N/A"}]
        
        # 3. Hypotheses
        hyp_val = find_value(["hypotheses", "proposed_hypotheses"], data)
        normalized["hypotheses"] = []
        
        if hyp_val and isinstance(hyp_val, list):
            for hyp_item in hyp_val:
                if isinstance(hyp_item, dict):
                    hyp_data = {
                        "title": ensure_string(find_value(["title"], hyp_item)) or "Untitled",
                        "research_question": ensure_string(find_value(["research_question", "pico"], hyp_item)) or "N/A",
                        "rationale": ensure_string(find_value(["rationale"], hyp_item)) or "N/A",
                        "study_design": ensure_string(find_value(["study_design"], hyp_item)) or "Active Comparator New User Design",
                    }
                    
                    # TTE Components
                    if include_tte:
                        ttc_raw = find_value(["target_trial_components"], hyp_item) or {}
                        hyp_data["target_trial_components"] = {
                            "population": ensure_string(find_value(["population"], ttc_raw)) or "Not specified",
                            "intervention": ensure_string(find_value(["intervention"], ttc_raw)) or "Not specified",
                            "comparator": ensure_string(find_value(["comparator"], ttc_raw)) or "Not specified",
                            "outcome_operational_def": ensure_string(find_value(["outcome_operational_def", "outcome"], ttc_raw)) or "Not specified",
                            "follow_up": ensure_string(find_value(["follow_up"], ttc_raw)) or "Not specified",
                            "time_zero_definition": ensure_string(find_value(["time_zero_definition"], ttc_raw)) or "Date of first prescription"
                        }
                    else:
                        hyp_data["target_trial_components"] = {
                            "population": "N/A", "intervention": "N/A", "comparator": "N/A",
                            "outcome_operational_def": "N/A", "follow_up": "N/A", "time_zero_definition": "N/A"
                        }
                    
                    # Bias Mitigation
                    if include_bias:
                        bm_raw = find_value(["bias_mitigation"], hyp_item) or {}
                        confounders = find_value(["key_confounders"], bm_raw)
                        if isinstance(confounders, str):
                            confounders = [confounders]
                        elif not isinstance(confounders, list):
                            confounders = ["Age", "Sex", "Comorbidities"]
                        
                        hyp_data["bias_mitigation"] = {
                            "key_confounders": confounders,
                            "negative_control_outcome": ensure_string(find_value(["negative_control_outcome"], bm_raw)) or "N/A",
                            "sensitivity_analysis": ensure_string(find_value(["sensitivity_analysis"], bm_raw)) or "E-value"
                        }
                    else:
                        hyp_data["bias_mitigation"] = {
                            "key_confounders": [], "negative_control_outcome": "N/A", "sensitivity_analysis": "N/A"
                        }
                    
                    # Feasibility
                    if include_feasibility:
                        fa_raw = find_value(["feasibility_assessment"], hyp_item) or {}
                        hyp_data["feasibility_assessment"] = {
                            "data_source_suitability": ensure_string(find_value(["data_source_suitability"], fa_raw)) or "N/A",
                            "potential_challenges": ensure_string(find_value(["potential_challenges"], fa_raw)) or "N/A",
                            "expected_sample_size": ensure_string(find_value(["expected_sample_size"], fa_raw)) or "Medium"
                        }
                    else:
                        hyp_data["feasibility_assessment"] = {
                            "data_source_suitability": "N/A", "potential_challenges": "N/A", "expected_sample_size": "N/A"
                        }
                    
                    normalized["hypotheses"].append(hyp_data)
        
        if not normalized["hypotheses"]:
            normalized["hypotheses"] = [{
                "title": "Hypothesis Generation Failed",
                "research_question": "Unable to generate",
                "rationale": "The model failed to produce structured hypotheses.",
                "study_design": "N/A",
                "target_trial_components": {
                    "population": "N/A", "intervention": "N/A", "comparator": "N/A",
                    "outcome_operational_def": "N/A", "follow_up": "N/A", "time_zero_definition": "N/A"
                },
                "bias_mitigation": {
                    "key_confounders": [], "negative_control_outcome": "N/A", "sensitivity_analysis": "N/A"
                },
                "feasibility_assessment": {
                    "data_source_suitability": "N/A", "potential_challenges": "N/A", "expected_sample_size": "N/A"
                }
            }]
        
        return normalized
