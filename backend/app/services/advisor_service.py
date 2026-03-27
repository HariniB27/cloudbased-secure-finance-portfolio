import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import re
from app.schemas.portfolio import AdvisorAdvice, PortfolioSummary, PortfolioFeatures, RiskPrediction
from app.config import get_settings

settings = get_settings()


class AdvisorService:
    """Service for LLM-based portfolio advice"""
    
    @staticmethod
    def get_advice(
        db: Session,
        user_id: int,
        summary: PortfolioSummary,
        features: PortfolioFeatures,
        risk: RiskPrediction
    ) -> AdvisorAdvice:
        """Generate portfolio advice using Gemini -> rule-based fallback."""
        return AdvisorService._generate_llm_advice(summary, features, risk)
    
    @staticmethod
    def _generate_mock_advice(
        summary: PortfolioSummary,
        features: PortfolioFeatures,
        risk: RiskPrediction
    ) -> AdvisorAdvice:
        """Generate deterministic advice based on rules (mock mode)"""
        
        # Portfolio health
        if summary.total_profit_loss_percentage > 10:
            health = f"Your portfolio is performing well with {summary.total_profit_loss_percentage:.1f}% returns. The current value of ₹{summary.total_current:,.0f} shows strong growth from your initial investment of ₹{summary.total_invested:,.0f}."
        elif summary.total_profit_loss_percentage > 0:
            health = f"Your portfolio shows modest positive returns of {summary.total_profit_loss_percentage:.1f}%. While growth is present, there's room for optimization."
        else:
            health = f"Your portfolio is currently down {abs(summary.total_profit_loss_percentage):.1f}%. This presents an opportunity to reassess and rebalance your holdings."
        
        # Risk reduction actions
        risk_actions = []
        if risk.risk_label == "HIGH":
            risk_actions.append("Consider reducing equity exposure by 10-15% to lower volatility")
            risk_actions.append("Increase allocation to debt instruments or fixed deposits for stability")
            if features.concentration_hhi > 0.3:
                risk_actions.append("Your portfolio is highly concentrated - diversify across more assets")
        elif risk.risk_label == "MODERATE":
            risk_actions.append("Maintain current risk profile with periodic rebalancing")
            risk_actions.append("Review individual stock holdings for company-specific risks")
        else:  # LOW
            if features.equity_allocation < 0.3:
                risk_actions.append("Consider increasing equity allocation for higher growth potential")
            risk_actions.append("Current risk level is well-managed - maintain diversification")
        
        # Diversification insights
        div_insights = []
        if features.equity_allocation > 0.6:
            div_insights.append(f"High equity concentration at {features.equity_allocation*100:.1f}% - consider adding bonds or gold")
        if features.cash_allocation > 0.3:
            div_insights.append(f"Significant cash allocation at {features.cash_allocation*100:.1f}% - deploy into productive assets")
        if features.commodity_allocation < 0.05:
            div_insights.append("Add 5-10% in gold/silver for inflation hedge and diversification")
        if len(div_insights) == 0:
            div_insights.append("Asset allocation is well-balanced across equity, debt, and commodities")
        
        # Scenario insights
        if risk.risk_label == "HIGH":
            scenario = "In a market correction, your portfolio could see drawdowns of 15-25%. Consider hedging with debt instruments."
        elif risk.risk_label == "MODERATE":
            scenario = "During market volatility, expect 8-15% fluctuations. Your balanced approach provides reasonable downside protection."
        else:
            scenario = "Your conservative allocation limits downside to 5-10% in adverse conditions, though upside may also be capped."
        
        # Strategy recommendation
        if summary.total_profit_loss_percentage > 5 and risk.risk_label != "HIGH":
            strategy = "Continue current strategy with quarterly rebalancing. Consider booking partial profits in top performers."
        elif risk.risk_label == "HIGH":
            strategy = "Rebalance portfolio towards 50-60% equity, 30-40% debt, 10% commodities for risk-adjusted growth."
        else:
            strategy = "Increase equity exposure gradually through SIPs in diversified index funds for long-term wealth creation."
        
        return AdvisorAdvice(
            portfolio_health=health,
            risk_reduction_actions=risk_actions,
            diversification_insights=div_insights,
            scenario_insights=scenario,
            strategy_recommendation=strategy,
            provider="Rule-based Model",
            model="rules",
            generated_at=datetime.now(timezone.utc)
        )
    
    @staticmethod
    def _generate_llm_advice(
        summary: PortfolioSummary,
        features: PortfolioFeatures,
        risk: RiskPrediction
    ) -> AdvisorAdvice:
        """Generate advice using Gemini primary, rule-based fallback."""
        context = AdvisorService._build_context(summary, features, risk)
        prompt = AdvisorService._build_prompt(context, risk_json=risk.model_dump())

        # Gemini primary
        try:
            if settings.GEMINI_API_KEY:
                print("Advisor LLM: using Gemini (primary).")
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)
                resp = model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.3},
                )
                text = getattr(resp, "text", None) or ""
                gemini_json = AdvisorService._safe_json_parse(text)
                print("Advisor LLM: Gemini response received.")
                return AdvisorService._to_advice(gemini_json, provider="Gemini", model=settings.GEMINI_MODEL)
            else:
                print("Advisor LLM: GEMINI_API_KEY not set; skipping Gemini.")
        except Exception as e:
            print(f"Advisor LLM: Gemini failed; error={str(e)}")

        # Final fallback: rule-based
        return AdvisorService._generate_mock_advice(summary, features, risk)

    @staticmethod
    def _build_context(summary: PortfolioSummary, features: PortfolioFeatures, risk: RiskPrediction) -> Dict[str, Any]:
        return {
            "total_invested": summary.total_invested,
            "total_current": summary.total_current,
            "profit_loss_pct": summary.total_profit_loss_percentage,
            "risk_label": risk.risk_label,
            "risk_confidence": risk.confidence,
            "equity_allocation": features.equity_allocation * 100,
            "debt_allocation": features.debt_allocation * 100,
            "commodity_allocation": features.commodity_allocation * 100,
            "cash_allocation": features.cash_allocation * 100,
            "concentration": features.concentration_hhi,
            "volatility": features.volatility_proxy
        }

    @staticmethod
    def _build_prompt(context: Dict[str, Any], risk_json: Dict[str, Any]) -> str:
        return f"""You are a professional financial advisor generating structured, realistic, and practical portfolio advice for Indian retail investors.

Portfolio Summary:
- Total Invested: ₹{context['total_invested']:,.0f}
- Current Value: ₹{context['total_current']:,.0f}
- Returns: {context['profit_loss_pct']:.1f}%
- Risk Level: {context['risk_label']} (confidence: {context['risk_confidence']:.0%})

Asset Allocation:
- Equity: {context['equity_allocation']:.1f}%
- Debt/MF: {context['debt_allocation']:.1f}%
- Commodities: {context['commodity_allocation']:.1f}%
- Cash: {context['cash_allocation']:.1f}%

Portfolio Metrics:
- Concentration (HHI): {context['concentration']:.3f}
- Volatility Proxy: {context['volatility']:.3f}

Risk JSON (input data):
{json.dumps(risk_json, ensure_ascii=False)}

Instructions:
- Use ONLY the data provided above (do not assume hidden holdings).
- Keep advice realistic, practical, and slightly conservative.
- Do NOT assume user age, salary, goals, or time horizon unless provided.
- Avoid alarmist words like "urgent" or "critical".
- Avoid generic statements without explanation.
- Refer to the actual allocation/risk/returns values in your reasoning.
- Provide India-context suggestions (large-cap funds, short-term debt funds, FDs, gold) without legal or tax guarantees.

Required content:
1) Portfolio Health
- Briefly assess performance in context of risk level.
- Identify the single biggest risk factor (e.g., concentration, volatility, cash drag).

2) Priority Actions (MOST IMPORTANT)
- Provide 3-5 prioritized, numbered actions in order.
- Each action must include:
  - what to do
  - one-line why it matters

3) Risk Strategy
- Suggest realistic rebalancing ranges (percentage bands).
- Avoid extreme or unrealistic changes.

4) Diversification
- Identify underweighted or missing categories with specific examples.

5) Scenarios
- Include one downside scenario and one opportunity scenario.

6) Recommendation
- Provide a clear long-term approach including SIP, rebalancing cadence, and discipline.

Output rules:
- Return ONLY valid JSON (no markdown, no backticks, no extra text).
- Arrays must contain 2-5 items each.
- Each bullet/action should be a single sentence.

Return ONLY valid JSON with these exact keys:
- portfolio_health: A 2-3 sentence assessment
- risk_reduction_actions: Array of 2-5 specific actions
- diversification_insights: Array of 2-5 insights
- scenario_insights: One paragraph on potential scenarios
- strategy_recommendation: One paragraph with actionable strategy

Example JSON shape (values are examples; compute your own from the input):
{{
  "portfolio_health": "…",
  "risk_reduction_actions": ["…", "…"],
  "diversification_insights": ["…", "…"],
  "scenario_insights": "…",
  "strategy_recommendation": "…"
}}
"""

    @staticmethod
    def _safe_json_parse(text: str) -> Dict[str, Any]:
        """
        Parse JSON from an LLM response robustly:
        - Strips markdown code fences
        - Extracts the first JSON object if extra text exists
        """
        if not text:
            return {}
        cleaned = text.strip()
        # Remove ```json ... ``` fences
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        # If it isn't pure JSON, try extracting first {...} block.
        if not (cleaned.startswith("{") and cleaned.endswith("}")):
            extracted = AdvisorService._extract_first_json_object(cleaned)
            if extracted:
                cleaned = extracted

        try:
            return json.loads(cleaned)
        except Exception as e:
            print(f"Advisor LLM: JSON parse failed; error={e}; sample={cleaned[:200]!r}")
            return {}

    @staticmethod
    def _extract_first_json_object(text: str) -> Optional[str]:
        """Extract the first balanced JSON object from text."""
        start = text.find("{")
        if start == -1:
            return None
        depth = 0
        in_str = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == "\"":
                    in_str = False
                continue
            else:
                if ch == "\"":
                    in_str = True
                    continue
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start : i + 1]
        return None

    @staticmethod
    def _to_advice(advice_json: Dict[str, Any], provider: str, model: str) -> AdvisorAdvice:
        # Defensive parsing so we don't crash if LLM output is malformed.
        portfolio_health = advice_json.get("portfolio_health") or "Unable to generate advice."
        risk_reduction_actions = advice_json.get("risk_reduction_actions") or []
        diversification_insights = advice_json.get("diversification_insights") or []
        scenario_insights = advice_json.get("scenario_insights") or ""
        strategy_recommendation = advice_json.get("strategy_recommendation") or ""
        return AdvisorAdvice(
            portfolio_health=portfolio_health,
            risk_reduction_actions=risk_reduction_actions,
            diversification_insights=diversification_insights,
            scenario_insights=scenario_insights,
            strategy_recommendation=strategy_recommendation,
            provider=provider,
            model=model,
            generated_at=datetime.now(timezone.utc)
        )
