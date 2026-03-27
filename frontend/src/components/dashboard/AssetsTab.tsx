import { useEffect, useState } from "react";
import { Loader2, Plus, Pencil, Trash2, TrendingUp, TrendingDown } from "lucide-react";
import { getAssets, deleteAsset } from "@/lib/api";
import { formatINR, formatPercent } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";
import AddAssetModal from "./AddAssetModal";
import EditAssetModal from "./EditAssetModal";

interface Asset {
  id: number | string;
  name: string;
  asset_type: string;
  invested_amount: number;
  current_value: number;
  symbol?: string;
  quantity?: number;
  exchange?: string;
  karat?: string;
  interest_rate?: number;
  term_months?: number;
  interest_type?: string;
  purchase_date?: string;
  [key: string]: unknown;
}

const typeBadge = (type: string) => {
  const cls: Record<string, string> = {
    equity: "badge-equity", debt: "badge-debt", gold: "badge-gold",
    silver: "badge-silver", cash: "badge-cash",
  };
  return <span className={cls[type] || "badge-equity"}>{type.charAt(0).toUpperCase() + type.slice(1)}</span>;
};

const AssetsTab = ({ refreshKey }: { refreshKey: number }) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [addOpen, setAddOpen] = useState(false);
  const [editAsset, setEditAsset] = useState<Asset | null>(null);
  const { toast } = useToast();

  const fetchAssets = () => {
    setLoading(true);
    getAssets().then((res) => setAssets(res.data)).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(fetchAssets, [refreshKey]);

  const handleDelete = async (id: string | number) => {
    if (!window.confirm("Are you sure you want to delete this asset?")) return;
    try {
      await deleteAsset(id);
      toast({ title: "Asset deleted" });
      fetchAssets();
    } catch {
      toast({ title: "Failed to delete asset", variant: "destructive" });
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  return (
    <div className="animate-fade-in space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-foreground">Your Assets</h2>
        <Button onClick={() => setAddOpen(true)}><Plus className="h-4 w-4 mr-2" />Add Asset</Button>
      </div>

      {assets.length === 0 ? (
        <div className="card-elevated p-12 text-center">
          <p className="text-muted-foreground">No assets yet. Add your first investment!</p>
        </div>
      ) : (
        <div className="card-elevated overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Asset Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Investment Date</TableHead>
                <TableHead className="text-right">Invested Value</TableHead>
                <TableHead className="text-right">Current Value</TableHead>
                <TableHead className="text-right">Gain/Loss</TableHead>
                <TableHead className="text-right">Gain/Loss %</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {assets.map((a) => {
                const gl = a.current_value - a.invested_amount;
                const glPct = a.invested_amount ? (gl / a.invested_amount) * 100 : 0;
                const pos = gl >= 0;
                return (
                  <TableRow key={a.id}>
                    <TableCell className="font-medium">{a.name}</TableCell>
                    <TableCell>{typeBadge(a.asset_type)}</TableCell>
                    <TableCell>{a.purchase_date ? new Date(a.purchase_date).toLocaleDateString() : "N/A"}</TableCell>
                    <TableCell className="text-right">{formatINR(a.invested_amount)}</TableCell>
                    <TableCell className="text-right">{formatINR(a.current_value)}</TableCell>
                    <TableCell className="text-right">
                      <span className={pos ? "gain-positive" : "gain-negative"}>
                        <span className="inline-flex items-center gap-1">
                          {pos ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                          {pos ? "+" : ""}{formatINR(gl)}
                        </span>
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <span className={pos ? "gain-positive" : "gain-negative"}>{formatPercent(glPct)}</span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon" onClick={() => setEditAsset(a)}><Pencil className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(a.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}

      <AddAssetModal open={addOpen} onClose={() => setAddOpen(false)} onSuccess={fetchAssets} />
      {editAsset && <EditAssetModal asset={editAsset} onClose={() => setEditAsset(null)} onSuccess={fetchAssets} />}
    </div>
  );
};

export default AssetsTab;
