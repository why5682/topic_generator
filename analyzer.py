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
    hypotheses: List[Hypothesis] = Field(description="3 TTE-based research proposals")


class TrendAnalyzer:
    def __init__(self, model_name: str, ollama_client=None): 
        self.model_name = model_name
        self.client = ollama_client

    def analyze_and_hypothesize(self, abstracts: List[dict], topic: str) -> TrendAnalysisResult:
        if not abstracts:
            return TrendAnalysisResult(
                landscape_summary="No data provided.",
                identified_gaps=[],
                hypotheses=[]
            )

        context_text = ""
        for i, paper in enumerate(abstracts):
            context_text += f"[{i+1}] Title: {paper['title']}\nAbstract: {paper['abstract']}\n\n"

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
- Key limitations mentioned in abstracts (e.g., residual confounding, small sample size).

## STEP 2: GAP & FEASIBILITY IDENTIFICATION
Categorize gaps into:
1. **Comparator Gaps**: Lack of active comparator designs (avoid placebo comparisons).
2. **Population Gaps**: Subgroups like elderly (≥75), renal impairment, or specific comorbidities.
3. **Outcome Gaps**: Hard endpoints (hospitalization, mortality) vs. symptoms.
4. **Temporal Gaps**: Long-term safety (>5 years) or latency issues.

**CRITICAL FEASIBILITY FILTER**:
For every gap identified, ask: "Can this be studied in Claims/EMR?"
- ❌ DISCARD outcomes relying on subjective scores (e.g., pain scale, depression score) unless strictly coded.
- ✅ PRIORITIZE outcomes defined by ICD-10, Procedure codes, or Death registries.

## STEP 3: NOVELTY & VALIDITY CHECK
- ⚠️ Check: Is this ALREADY answered?
- ⚠️ Check: Is the "New User" design applicable? (Prevalent user bias risk).
- ⚠️ Check: Is there Clinical Equipoise between comparison groups?

## STEP 4: HYPOTHESIS GENERATION (Target Trial Emulation Framework)
Propose exactly 3 hypotheses. Focus on "Active Comparator New User Design".

Structure for each:
- **Title**: Academic format.
- **Research Question**: PICO format.
- **Rationale**: Cite specific gaps. Why is RWD better than RCT here?
- **TTE Components (Target Trial Emulation)**:
  * **Eligibility Criteria**: Inclusion/Exclusion (must be code-able).
  * **Treatment Strategies**: Index drug vs. Active Comparator (Must be same indication/severity level).
  * **Assignment**: Mimic randomization at index date (washout period required).
  * **Follow-up**: "Intention-to-treat" vs "Per-protocol" (As-treated) definition.
  * **Outcome**: Operational definition (e.g., "Primary diagnosis of [Code] in inpatient setting").
  * **Time Zero**: Index date definition.
  * **Causal Contrast**: Hazard Ratio / Risk Difference.
- **Bias Mitigation**:
  * **Confounding**: List key covariates for PS matching/IPTW.
  * **Falsification**: Suggest a "Negative Control Outcome" to check for unmeasured confounding.
  * **Sensitivity**: E-value or quantitative bias analysis approach.
- **Feasibility**: Data source suitability, sample size estimate, key challenges.

---
**OUTPUT FORMAT** (Strict JSON):
{{
    "landscape_summary": "Summary text describing current research landscape...",
    "identified_gaps": [
        {{
            "gap": "Specific description of evidence gap",
            "category": "Comparator/Population/Outcome/Temporal",
            "feasibility_status": "High/Medium/Low (with reason)"
        }}
    ],
    "hypotheses": [
        {{
            "title": "Publication-ready academic title",
            "research_question": "PICO format question",
            "rationale": "Why this study is needed now",
            "study_design": "Active Comparator New User Design",
            "target_trial_components": {{
                "population": "Code-able eligibility criteria",
                "intervention": "Index drug definition",
                "comparator": "Active comparator with equipoise justification",
                "outcome_operational_def": "Specific definition with codes",
                "follow_up": "Start/End/Censoring definition",
                "time_zero_definition": "Index date definition"
            }},
            "bias_mitigation": {{
                "key_confounders": ["Confounder 1", "Confounder 2", "..."],
                "negative_control_outcome": "Suggested falsification outcome",
                "sensitivity_analysis": "E-value or QBA approach"
            }},
            "feasibility_assessment": {{
                "data_source_suitability": "Why Claims/EMR fits",
                "potential_challenges": "Key limitations",
                "expected_sample_size": "Low/Medium/High"
            }}
        }}
    ]
}}

**ABSTRACTS TO ANALYZE**:
{context_text}

Think step by step. Ensure final output is ONLY valid JSON matching the exact structure above.
"""
        
        try:
            print(f"DEBUG: Sending TTE-based request to Ollama ({self.model_name})...")
            
            chat_func = self.client.chat if self.client else ollama.chat
            
            response = chat_func(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json', 
                options={'temperature': 0.7}
            )
            
            content = response['message']['content']
            print("DEBUG: Raw LLM Output start ---")
            print(content[:500])
            print("DEBUG: Raw LLM Output end ---")
            
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
                raise ValueError(f"LLM did not return valid JSON. Content: {content[:200]}...")

            # Normalize and validate
            normalized_data = self._normalize_response(data)
            
            return TrendAnalysisResult.model_validate(normalized_data)
            
        except Exception as e:
            print(f"DEBUG: Analysis error: {e}")
            return TrendAnalysisResult(
                landscape_summary=f"Analysis failed: {str(e)}",
                identified_gaps=[],
                hypotheses=[]
            )

    def _normalize_response(self, data: dict) -> dict:
        """Normalize LLM response to match expected structure."""
        
        def find_value(targets: List[str], source: dict):
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
        val = find_value(["landscape_summary", "trend_summary", "summary", "current_landscape"], data)
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
        hyp_val = find_value(["hypotheses", "proposed_hypotheses", "research_hypotheses"], data)
        normalized["hypotheses"] = []
        
        if hyp_val and isinstance(hyp_val, list):
            for hyp_item in hyp_val[:3]:  # Max 3
                if isinstance(hyp_item, dict):
                    # Target Trial Components
                    ttc_raw = find_value(["target_trial_components", "tte_components", "trial_components"], hyp_item) or {}
                    ttc = {
                        "population": ensure_string(find_value(["population", "eligibility", "inclusion"], ttc_raw)) or "Not specified",
                        "intervention": ensure_string(find_value(["intervention", "treatment", "exposure"], ttc_raw)) or "Not specified",
                        "comparator": ensure_string(find_value(["comparator", "control"], ttc_raw)) or "Not specified",
                        "outcome_operational_def": ensure_string(find_value(["outcome_operational_def", "outcome", "primary_outcome"], ttc_raw)) or "Not specified",
                        "follow_up": ensure_string(find_value(["follow_up", "followup", "follow_up_period"], ttc_raw)) or "Not specified",
                        "time_zero_definition": ensure_string(find_value(["time_zero_definition", "time_zero", "index_date"], ttc_raw)) or "Date of first prescription"
                    }
                    
                    # Bias Mitigation
                    bm_raw = find_value(["bias_mitigation", "bias", "confounding_control"], hyp_item) or {}
                    confounders = find_value(["key_confounders", "confounders", "covariates"], bm_raw)
                    if isinstance(confounders, str):
                        confounders = [confounders]
                    elif not isinstance(confounders, list):
                        confounders = ["Age", "Sex", "Comorbidities"]
                    
                    bm = {
                        "key_confounders": confounders,
                        "negative_control_outcome": ensure_string(find_value(["negative_control_outcome", "falsification", "negative_control"], bm_raw)) or "Ingrown toenail or similar",
                        "sensitivity_analysis": ensure_string(find_value(["sensitivity_analysis", "sensitivity", "e_value"], bm_raw)) or "E-value calculation"
                    }
                    
                    # Feasibility
                    fa_raw = find_value(["feasibility_assessment", "feasibility"], hyp_item) or {}
                    fa = {
                        "data_source_suitability": ensure_string(find_value(["data_source_suitability", "data_source", "suitability"], fa_raw)) or "Claims data appropriate",
                        "potential_challenges": ensure_string(find_value(["potential_challenges", "challenges", "limitations"], fa_raw)) or "Standard RWD limitations apply",
                        "expected_sample_size": ensure_string(find_value(["expected_sample_size", "sample_size"], fa_raw)) or "Medium"
                    }
                    
                    normalized["hypotheses"].append({
                        "title": ensure_string(find_value(["title", "hypothesis_title"], hyp_item)) or "Untitled Hypothesis",
                        "research_question": ensure_string(find_value(["research_question", "pico", "question"], hyp_item)) or "Research question not specified",
                        "rationale": ensure_string(find_value(["rationale", "justification", "background"], hyp_item)) or "Rationale not provided",
                        "study_design": ensure_string(find_value(["study_design", "design"], hyp_item)) or "Active Comparator New User Design",
                        "target_trial_components": ttc,
                        "bias_mitigation": bm,
                        "feasibility_assessment": fa
                    })
        
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
