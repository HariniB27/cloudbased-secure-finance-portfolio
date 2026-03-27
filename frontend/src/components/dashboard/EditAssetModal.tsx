import { useState } from "react";
import { Loader2 } from "lucide-react";
import { updateAsset } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";

interface EditAsset {
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

const EditAssetModal = ({ asset, onClose, onSuccess }: { asset: EditAsset; onClose: () => void; onSuccess: () => void }) => {
  const [name, setName] = useState(asset.name);
  const [symbol, setSymbol] = useState(String(asset.symbol || ""));
  const [quantity, setQuantity] = useState<number | "">(asset.quantity ?? "");
  const [exchange, setExchange] = useState(String(asset.exchange || ""));
  const [karat, setKarat] = useState(String(asset.karat || ""));
  const [interestRate, setInterestRate] = useState<number | "">(asset.interest_rate ?? "");
  const [termMonths, setTermMonths] = useState<number | "">(asset.term_months ?? "");
  const [interestType, setInterestType] = useState(String(asset.interest_type || ""));
  const [purchaseDate, setPurchaseDate] = useState(
    asset.purchase_date ? new Date(asset.purchase_date).toISOString().slice(0, 10) : ""
  );
  // Add-form parity fields (derived invested amount inputs)
  const [costPerShare, setCostPerShare] = useState<number | "">("");
  const [pricePerGram, setPricePerGram] = useState<number | "">("");
  const [costValue, setCostValue] = useState<number | "">(asset.asset_type === "debt" || asset.asset_type === "mutual_fund" ? asset.invested_amount : "");
  const [depositAmount, setDepositAmount] = useState<number | "">(asset.asset_type === "cash" ? asset.invested_amount : "");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async () => {
    if (!window.confirm("Are you sure you want to update this asset?")) return;
    setLoading(true);
    try {
      const payload: Record<string, unknown> = {
        name,
        purchase_date: purchaseDate ? new Date(`${purchaseDate}T00:00:00Z`).toISOString() : null,
      };

      if (asset.asset_type === "equity") {
        payload.symbol = symbol || null;
        payload.exchange = exchange || null;
        payload.quantity = quantity === "" ? null : Number(quantity);
        const invested = (Number(payload.quantity) || 0) * (Number(costPerShare) || 0);
        payload.invested_amount = invested > 0 ? invested : null;
      } else if (asset.asset_type === "debt" || asset.asset_type === "mutual_fund") {
        payload.symbol = symbol || null;
        payload.quantity = quantity === "" ? null : Number(quantity);
        payload.invested_amount = costValue === "" ? null : Number(costValue);
      } else if (asset.asset_type === "gold") {
        payload.karat = karat || null;
        payload.quantity = quantity === "" ? null : Number(quantity);
        const invested = (Number(payload.quantity) || 0) * (Number(pricePerGram) || 0);
        payload.invested_amount = invested > 0 ? invested : null;
      } else if (asset.asset_type === "silver") {
        payload.quantity = quantity === "" ? null : Number(quantity);
        const invested = (Number(payload.quantity) || 0) * (Number(pricePerGram) || 0);
        payload.invested_amount = invested > 0 ? invested : null;
      } else if (asset.asset_type === "cash") {
        payload.interest_rate = interestRate === "" ? null : Number(interestRate);
        payload.term_months = termMonths === "" ? null : Number(termMonths);
        payload.interest_type = interestType || null;
        payload.invested_amount = depositAmount === "" ? null : Number(depositAmount);
      }

      await updateAsset(asset.id, {
        ...payload,
      });
      toast({ title: "Asset updated!" });
      onSuccess();
      onClose();
    } catch (err: any) {
      toast({ title: "Error", description: err.response?.data?.detail || "Update failed", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader><DialogTitle>Edit Asset</DialogTitle></DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2"><Label>Name</Label><Input value={name} onChange={(e) => setName(e.target.value)} /></div>
          <div className="space-y-2"><Label>Investment Date</Label><Input type="date" value={purchaseDate} onChange={(e) => setPurchaseDate(e.target.value)} /></div>

          {(asset.asset_type === "equity" || asset.asset_type === "debt" || asset.asset_type === "mutual_fund") && (
            <div className="space-y-2"><Label>Symbol</Label><Input value={symbol} onChange={(e) => setSymbol(e.target.value)} /></div>
          )}
          {(asset.asset_type === "equity" || asset.asset_type === "debt" || asset.asset_type === "mutual_fund" || asset.asset_type === "gold" || asset.asset_type === "silver") && (
            <div className="space-y-2"><Label>Quantity</Label><Input type="number" value={quantity} onChange={(e) => setQuantity(e.target.value ? Number(e.target.value) : "")} /></div>
          )}
          {asset.asset_type === "equity" && (
            <>
              <div className="space-y-2"><Label>Exchange</Label><Input value={exchange} onChange={(e) => setExchange(e.target.value)} /></div>
              <div className="space-y-2"><Label>Cost per Share (₹)</Label><Input type="number" value={costPerShare} onChange={(e) => setCostPerShare(e.target.value ? Number(e.target.value) : "")} /></div>
            </>
          )}
          {asset.asset_type === "gold" && (
            <>
              <div className="space-y-2"><Label>Karat</Label><Input value={karat} onChange={(e) => setKarat(e.target.value)} /></div>
              <div className="space-y-2"><Label>Price per Gram (₹)</Label><Input type="number" value={pricePerGram} onChange={(e) => setPricePerGram(e.target.value ? Number(e.target.value) : "")} /></div>
            </>
          )}
          {asset.asset_type === "silver" && (
            <div className="space-y-2"><Label>Price per Gram (₹)</Label><Input type="number" value={pricePerGram} onChange={(e) => setPricePerGram(e.target.value ? Number(e.target.value) : "")} /></div>
          )}
          {(asset.asset_type === "debt" || asset.asset_type === "mutual_fund") && (
            <div className="space-y-2"><Label>Cost Value (₹)</Label><Input type="number" value={costValue} onChange={(e) => setCostValue(e.target.value ? Number(e.target.value) : "")} /></div>
          )}
          {asset.asset_type === "cash" && (
            <>
              <div className="space-y-2"><Label>Deposit Amount (₹)</Label><Input type="number" value={depositAmount} onChange={(e) => setDepositAmount(e.target.value ? Number(e.target.value) : "")} /></div>
              <div className="space-y-2"><Label>Interest Rate (%)</Label><Input type="number" value={interestRate} onChange={(e) => setInterestRate(e.target.value ? Number(e.target.value) : "")} /></div>
              <div className="space-y-2"><Label>Term (months)</Label><Input type="number" value={termMonths} onChange={(e) => setTermMonths(e.target.value ? Number(e.target.value) : "")} /></div>
              <div className="space-y-2"><Label>Interest Type</Label><Input value={interestType} onChange={(e) => setInterestType(e.target.value)} /></div>
            </>
          )}
          <Button onClick={handleSubmit} className="w-full" disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Update Asset
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EditAssetModal;
