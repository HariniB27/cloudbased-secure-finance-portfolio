import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { getPerformanceMetrics } from "@/lib/api";
import { formatINR, formatPercent } from "@/lib/format";

interface AssetPerformance {
  asset_id: number;
  name: string;
  asset_type: string;
  return_percentage: number;
  gain_loss: number;
}

interface PerformanceData {
  absolute_return_percentage: number;
  annualized_return_percentage: number;
  best_performing_asset: AssetPerformance | null;
  worst_performing_asset: AssetPerformance | null;
}

const PerformanceTab = ({ refreshKey }: { refreshKey: number }) => {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getPerformanceMetrics()
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [refreshKey]);

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  if (!data) {
    return <p className="text-center text-muted-foreground py-10">No performance data available.</p>;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
      <div className="card-elevated p-8 space-y-2">
        <p className="text-sm text-muted-foreground">Absolute Return</p>
        <p className="text-3xl font-bold text-foreground">{formatPercent(data.absolute_return_percentage)}</p>
        <p className="text-sm text-muted-foreground">Annualized Return</p>
        <p className="text-2xl font-semibold text-foreground">{formatPercent(data.annualized_return_percentage)}</p>
        <p className="text-xs text-muted-foreground">Calculated using each asset's added date.</p>
      </div>
      <div className="card-elevated p-8 space-y-5">
        <div>
          <p className="text-sm text-muted-foreground">Best Performing Asset</p>
          <p className="text-lg font-semibold text-foreground">{data.best_performing_asset?.name || "N/A"}</p>
          <p className="text-sm text-muted-foreground">
            {data.best_performing_asset ? `${formatPercent(data.best_performing_asset.return_percentage)} (${formatINR(data.best_performing_asset.gain_loss)})` : ""}
          </p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Worst Performing Asset</p>
          <p className="text-lg font-semibold text-foreground">{data.worst_performing_asset?.name || "N/A"}</p>
          <p className="text-sm text-muted-foreground">
            {data.worst_performing_asset ? `${formatPercent(data.worst_performing_asset.return_percentage)} (${formatINR(data.worst_performing_asset.gain_loss)})` : ""}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PerformanceTab;
