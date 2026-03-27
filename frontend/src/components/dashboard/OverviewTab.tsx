import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Loader2 } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { getPortfolioSummary } from "@/lib/api";
import { formatINR, formatGainLoss, formatPercent } from "@/lib/format";

interface SummaryData {
  total_invested: number;
  total_current: number;
  total_profit_loss: number;
  allocation_breakdown: Record<string, number>;
  last_refreshed: string;
}

const COLORS = {
  Equity: "hsl(217, 91%, 60%)",
  "Mutual Funds": "hsl(160, 84%, 39%)",
  Commodities: "hsl(38, 92%, 50%)",
  Cash: "hsl(258, 90%, 66%)",
};

const OverviewTab = ({ refreshKey }: { refreshKey: number }) => {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getPortfolioSummary()
      .then((res) => setSummary(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [refreshKey]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!summary) {
    return <p className="text-center text-muted-foreground py-10">No portfolio data available.</p>;
  }

  const ab = summary.allocation_breakdown || {};
  const equity = ab.equity || 0;
  const mutualFunds = (ab.debt || 0) + (ab.mutual_fund || 0);
  const commodities = (ab.gold || 0) + (ab.silver || 0);
  const cash = ab.cash || 0;

  const pieData = [
    { name: "Equity", value: equity },
    { name: "Mutual Funds", value: mutualFunds },
    { name: "Commodities", value: commodities },
    { name: "Cash", value: cash },
  ].filter((d) => d.value > 0);

  const totalAlloc = pieData.reduce((s, d) => s + d.value, 0);
  const isPositive = summary.total_profit_loss >= 0;
  const pctChange = summary.total_invested
    ? (summary.total_profit_loss / summary.total_invested) * 100
    : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
      {/* Total Portfolio Value */}
      <div className="card-elevated p-8">
        <p className="text-sm text-muted-foreground mb-1">Total Portfolio Value</p>
        <p className="text-4xl font-bold text-foreground mb-3">{formatINR(summary.total_current)}</p>
        <p className="text-sm text-muted-foreground mb-2">
          Total Invested: <span className="text-foreground font-medium">{formatINR(summary.total_invested)}</span>
        </p>
        <p className="text-xs text-muted-foreground mb-3">
          Last Refresh: {summary.last_refreshed ? new Date(summary.last_refreshed).toLocaleString() : "N/A"}
        </p>
        <div className={`inline-flex items-center gap-1 text-sm ${isPositive ? "gain-positive" : "gain-negative"}`}>
          {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
          <span>
            {formatGainLoss(summary.total_profit_loss)} ({formatPercent(pctChange)})
          </span>
        </div>
      </div>

      {/* Allocation Pie */}
      <div className="card-elevated p-8">
        <p className="text-sm text-muted-foreground mb-4">Portfolio Allocation</p>
        {pieData.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">No allocation data</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={95}
                paddingAngle={3}
                dataKey="value"
                label={({ name, value }) => `${name} ${totalAlloc ? ((value / totalAlloc) * 100).toFixed(0) : 0}%`}
                labelLine={false}
              >
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS]} />
                ))}
              </Pie>
              <Tooltip formatter={(val: number) => `${totalAlloc ? ((val / totalAlloc) * 100).toFixed(1) : 0}%`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};

export default OverviewTab;
