import { useEffect, useState } from "react";
import { Loader2, Sparkles, RefreshCw } from "lucide-react";
import { predictRisk, getAdvice } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface RiskData {
  risk_label: string;
  confidence: number;
  features_used: {
    equity_allocation: number;
    debt_allocation: number;
    commodity_allocation: number;
    cash_allocation: number;
    volatility_proxy: number;
  };
}

interface AdviceData {
  diversification_insights: string[];
  risk_reduction_actions: string[];
  scenario_insights: string;
  strategy_recommendation: string;
  portfolio_health: string;
  provider?: string;
  model?: string;
  generated_at?: string;
}

const riskColor: Record<string, string> = {
  LOW: "text-success",
  MODERATE: "text-warning",
  HIGH: "text-destructive",
};

const AllocationBar = ({ label, value }: { label: string; value: number }) => {
  const normalized = value <= 1 ? value * 100 : value;
  const pct = Math.round(Math.max(0, Math.min(100, normalized)));
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium text-foreground">{pct}%</span>
      </div>
      <div className="allocation-bar">
        <div className="allocation-bar-fill bg-foreground" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
};

const RiskAdvisorTab = ({ refreshKey }: { refreshKey: number }) => {
  const [risk, setRisk] = useState<RiskData | null>(null);
  const [advice, setAdvice] = useState<AdviceData | null>(null);
  const [riskLoading, setRiskLoading] = useState(true);
  const [adviceLoading, setAdviceLoading] = useState(false);
  const [showAdvice, setShowAdvice] = useState(false);

  useEffect(() => {
    setRiskLoading(true);
    setShowAdvice(false);
    setAdvice(null);
    predictRisk().then((res) => setRisk(res.data)).catch(() => {}).finally(() => setRiskLoading(false));
  }, [refreshKey]);

  const fetchAdvice = async () => {
    setAdviceLoading(true);
    try {
      const res = await getAdvice();
      setAdvice(res.data);
      setShowAdvice(true);
    } catch { }
    finally { setAdviceLoading(false); }
  };

  if (riskLoading) {
    return <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  const f = risk?.features_used;
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
      {/* Risk Analysis */}
      <div className="card-elevated p-8 space-y-6">
        <h3 className="font-semibold text-foreground text-lg">Risk Analysis</h3>
        {risk ? (
          <>
            <div>
              <p className="text-sm text-muted-foreground">Risk Level</p>
              <p className={`text-3xl font-bold ${riskColor[risk.risk_label] || "text-foreground"}`}>{risk.risk_label}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Confidence</p>
                <p className="text-xl font-semibold text-foreground">{(risk.confidence * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Volatility</p>
                <p className="text-xl font-semibold text-foreground">{(f?.volatility_proxy || 0).toFixed(3)}</p>
              </div>
            </div>
            <div className="space-y-4">
              <p className="text-sm font-medium text-foreground">Relative Risk Contribution</p>
              <AllocationBar label="Equity" value={f?.equity_allocation || 0} />
              <AllocationBar label="Debt" value={f?.debt_allocation || 0} />
              <AllocationBar label="Commodities" value={f?.commodity_allocation || 0} />
              <AllocationBar label="Cash" value={f?.cash_allocation || 0} />
            </div>
          </>
        ) : (
          <p className="text-muted-foreground">Unable to load risk data.</p>
        )}
      </div>

      {/* AI Advisor */}
      <div className="card-elevated p-8 space-y-6">
        <h3 className="font-semibold text-foreground text-lg">AI Advisor</h3>

        {!showAdvice && !adviceLoading && (
          <div className="flex flex-col items-center justify-center py-12">
            <Button size="lg" onClick={fetchAdvice} className="gap-2">
              <Sparkles className="h-5 w-5" />
              Generate AI Advice
            </Button>
          </div>
        )}

        {adviceLoading && (
          <div className="flex items-center justify-center py-12 gap-2 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin" />
            Generating...
          </div>
        )}

        {showAdvice && advice && (
          <div className="space-y-4">
            <div className="advisor-card">
              <p className="text-sm font-medium mb-1">Portfolio Health</p>
              <p className="text-sm text-muted-foreground">{advice.portfolio_health || "N/A"}</p>
            </div>
            <div className="advisor-card">
              <p className="text-sm font-medium mb-1">Risk Reduction Actions</p>
              <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
                {(advice.risk_reduction_actions || []).map((item, idx) => <li key={`risk-${idx}`}>{item}</li>)}
              </ul>
            </div>
            <div className="advisor-card">
              <p className="text-sm font-medium mb-1">Diversification Insights</p>
              <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
                {(advice.diversification_insights || []).map((item, idx) => <li key={`div-${idx}`}>{item}</li>)}
              </ul>
            </div>
            <div className="advisor-card">
              <p className="text-sm font-medium mb-1">Scenario Insights</p>
              <p className="text-sm text-muted-foreground">{advice.scenario_insights || "N/A"}</p>
            </div>
            <div className="advisor-card">
              <p className="text-sm font-medium mb-1">Strategy Recommendation</p>
              <p className="text-sm text-muted-foreground">{advice.strategy_recommendation || "N/A"}</p>
            </div>
            <div className="text-xs text-muted-foreground border rounded-md p-3">
              Provider: {advice.provider || "unknown"} | Model: {advice.model || "unknown"} | Generated:{" "}
              {advice.generated_at
                ? new Date(advice.generated_at).toLocaleString(undefined, {
                    year: "numeric",
                    month: "short",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                  })
                : "N/A"}
            </div>
            <Button variant="outline" size="sm" onClick={fetchAdvice} className="gap-2">
              <RefreshCw className="h-4 w-4" />Refresh Insights
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskAdvisorTab;
