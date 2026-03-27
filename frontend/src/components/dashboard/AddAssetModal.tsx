import { useState } from "react";
import { Loader2 } from "lucide-react";
import { addAsset } from "@/lib/api";
import { formatINR } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { CalendarIcon } from "lucide-react";
import { format, addMonths, isAfter, startOfDay } from "date-fns";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const AddAssetModal = ({ open, onClose, onSuccess }: Props) => {
  const [assetType, setAssetType] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Equity
  const [stockName, setStockName] = useState("");
  const [stockSymbol, setStockSymbol] = useState("");
  const [exchange, setExchange] = useState("");
  const [quantity, setQuantity] = useState<number | "">("");
  const [costPerShare, setCostPerShare] = useState<number | "">("");

  // Debt
  const [fundName, setFundName] = useState("");
  const [schemeCode, setSchemeCode] = useState("");
  const [units, setUnits] = useState<number | "">("");
  const [costValue, setCostValue] = useState<number | "">("");

  // Commodities
  const [commodityType, setCommodityType] = useState("");
  const [karat, setKarat] = useState("");
  const [weight, setWeight] = useState<number | "">("");
  const [pricePerGram, setPricePerGram] = useState<number | "">("");

  // Cash/FD
  const [depositName, setDepositName] = useState("");
  const [depositAmount, setDepositAmount] = useState<number | "">("");
  const [interestRate, setInterestRate] = useState<number | "">("");
  const [termMonths, setTermMonths] = useState<number | "">("");
  const [interestType, setInterestType] = useState("");
  const [purchaseDate, setPurchaseDate] = useState<Date>(new Date());

  const resetFields = () => {
    setAssetType("");
    setStockName(""); setStockSymbol(""); setExchange(""); setQuantity(""); setCostPerShare("");
    setFundName(""); setSchemeCode(""); setUnits(""); setCostValue("");
    setCommodityType(""); setKarat(""); setWeight(""); setPricePerGram("");
    setDepositName(""); setDepositAmount(""); setInterestRate(""); setTermMonths(""); setInterestType(""); setPurchaseDate(new Date());
  };

  const handleSubmit = async () => {
    let payload: Record<string, unknown> = {};
    const today = startOfDay(new Date());
    if (isAfter(startOfDay(purchaseDate), today)) return;

    if (assetType === "equity") {
      if (!stockName || !stockSymbol || !exchange || !quantity || !costPerShare) return;
      payload = {
        asset_type: "equity", name: stockName, symbol: stockSymbol.toUpperCase(),
        exchange, quantity: Number(quantity), invested_amount: Number(quantity) * Number(costPerShare),
        purchase_date: purchaseDate.toISOString(),
      };
    } else if (assetType === "debt") {
      if (!fundName || !units || !costValue) return;
      payload = {
        asset_type: "debt", name: fundName, symbol: schemeCode || "",
        quantity: Number(units), invested_amount: Number(costValue),
        purchase_date: purchaseDate.toISOString(),
      };
    } else if (assetType === "gold") {
      if (!karat || !weight || !pricePerGram) return;
      payload = {
        asset_type: "gold", name: `Gold ${karat}`, karat,
        quantity: Number(weight), invested_amount: Number(weight) * Number(pricePerGram),
        purchase_date: purchaseDate.toISOString(),
      };
    } else if (assetType === "silver") {
      if (!weight || !pricePerGram) return;
      payload = {
        asset_type: "silver", name: "Silver",
        quantity: Number(weight), invested_amount: Number(weight) * Number(pricePerGram),
        purchase_date: purchaseDate.toISOString(),
      };
    } else if (assetType === "cash") {
      if (!depositName || !depositAmount || !interestRate || !termMonths || !interestType) return;
      payload = {
        asset_type: "cash", name: depositName,
        invested_amount: Number(depositAmount), interest_rate: Number(interestRate),
        term_months: Number(termMonths), interest_type: interestType === "Compound Interest" ? "compound" : "simple",
        purchase_date: purchaseDate.toISOString(),
      };
    }

    setLoading(true);
    try {
      if (!window.confirm("Are you sure you want to add this asset?")) {
        setLoading(false);
        return;
      }
      await addAsset(payload);
      toast({ title: "Asset added successfully!" });
      resetFields();
      onSuccess();
      onClose();
    } catch (err: any) {
      toast({ title: "Error", description: err.response?.data?.detail || "Failed to add asset", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const equityTotal = (Number(quantity) || 0) * (Number(costPerShare) || 0);
  const commodityTotal = (Number(weight) || 0) * (Number(pricePerGram) || 0);
  const maturityDate = termMonths ? addMonths(purchaseDate, Number(termMonths)) : null;

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) { resetFields(); onClose(); } }}>
      <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Asset</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Asset Type</Label>
            <Select value={assetType} onValueChange={(v) => { setAssetType(v); setCommodityType(""); }}>
              <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="equity">Equity</SelectItem>
                <SelectItem value="debt">Debt (Mutual Funds)</SelectItem>
                <SelectItem value="commodities">Commodities</SelectItem>
                <SelectItem value="cash">Cash (Fixed Deposit)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {assetType === "equity" && (
            <>
              <div className="space-y-2">
                <Label>Investment Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !purchaseDate && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {purchaseDate ? format(purchaseDate, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={purchaseDate} onSelect={(d) => d && setPurchaseDate(d)} initialFocus className="p-3 pointer-events-auto" />
                  </PopoverContent>
                </Popover>
                {isAfter(startOfDay(purchaseDate), startOfDay(new Date())) && (
                  <p className="text-destructive text-xs">Investment date cannot be in the future</p>
                )}
              </div>
              <div className="space-y-2"><Label>Stock Name</Label><Input value={stockName} onChange={(e) => setStockName(e.target.value)} placeholder="e.g. Reliance Industries" required /></div>
              <div className="space-y-2"><Label>Stock Symbol</Label><Input value={stockSymbol} onChange={(e) => setStockSymbol(e.target.value.toUpperCase())} placeholder="e.g. RELIANCE" required /></div>
              <div className="space-y-2">
                <Label>Exchange</Label>
                <Select value={exchange} onValueChange={setExchange}>
                  <SelectTrigger><SelectValue placeholder="Select exchange" /></SelectTrigger>
                  <SelectContent><SelectItem value="NSE">NSE</SelectItem><SelectItem value="BSE">BSE</SelectItem></SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2"><Label>Quantity</Label><Input type="number" value={quantity} onChange={(e) => setQuantity(e.target.value ? Number(e.target.value) : "")} min={1} /></div>
                <div className="space-y-2"><Label>Cost per Share (₹)</Label><Input type="number" value={costPerShare} onChange={(e) => setCostPerShare(e.target.value ? Number(e.target.value) : "")} min={0} /></div>
              </div>
              {equityTotal > 0 && <p className="text-sm text-muted-foreground">Total: {formatINR(equityTotal)}</p>}
            </>
          )}

          {assetType === "debt" && (
            <>
              <div className="space-y-2">
                <Label>Investment Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !purchaseDate && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {purchaseDate ? format(purchaseDate, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={purchaseDate} onSelect={(d) => d && setPurchaseDate(d)} initialFocus className="p-3 pointer-events-auto" />
                  </PopoverContent>
                </Popover>
                {isAfter(startOfDay(purchaseDate), startOfDay(new Date())) && (
                  <p className="text-destructive text-xs">Investment date cannot be in the future</p>
                )}
              </div>
              <div className="space-y-2"><Label>Mutual Fund Name</Label><Input value={fundName} onChange={(e) => setFundName(e.target.value)} placeholder="e.g. HDFC Mid-Cap Fund" required /></div>
              <div className="space-y-2"><Label>Scheme Code (optional)</Label><Input value={schemeCode} onChange={(e) => setSchemeCode(e.target.value)} placeholder="e.g. 119551" /></div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2"><Label>Number of Units</Label><Input type="number" value={units} onChange={(e) => setUnits(e.target.value ? Number(e.target.value) : "")} min={0} /></div>
                <div className="space-y-2"><Label>Cost Value (₹)</Label><Input type="number" value={costValue} onChange={(e) => setCostValue(e.target.value ? Number(e.target.value) : "")} min={0} /></div>
              </div>
            </>
          )}

          {assetType === "commodities" && (
            <>
              <div className="space-y-2">
                <Label>Commodity Type</Label>
                <Select value={commodityType} onValueChange={(v) => { setCommodityType(v); setAssetType(v === "Gold" ? "gold" : "silver"); }}>
                  <SelectTrigger><SelectValue placeholder="Select commodity" /></SelectTrigger>
                  <SelectContent><SelectItem value="Gold">Gold</SelectItem><SelectItem value="Silver">Silver</SelectItem></SelectContent>
                </Select>
              </div>
            </>
          )}

          {assetType === "gold" && (
            <>
              <div className="space-y-2">
                <Label>Investment Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !purchaseDate && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {purchaseDate ? format(purchaseDate, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={purchaseDate} onSelect={(d) => d && setPurchaseDate(d)} initialFocus className="p-3 pointer-events-auto" />
                  </PopoverContent>
                </Popover>
                {isAfter(startOfDay(purchaseDate), startOfDay(new Date())) && (
                  <p className="text-destructive text-xs">Investment date cannot be in the future</p>
                )}
              </div>
              <div className="space-y-2">
                <Label>Karat</Label>
                <Select value={karat} onValueChange={setKarat}>
                  <SelectTrigger><SelectValue placeholder="Select karat" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="24K">24K</SelectItem><SelectItem value="22K">22K</SelectItem>
                    <SelectItem value="18K">18K</SelectItem><SelectItem value="14K">14K</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2"><Label>Weight (grams)</Label><Input type="number" value={weight} onChange={(e) => setWeight(e.target.value ? Number(e.target.value) : "")} min={0} /></div>
                <div className="space-y-2"><Label>Price per Gram (₹)</Label><Input type="number" value={pricePerGram} onChange={(e) => setPricePerGram(e.target.value ? Number(e.target.value) : "")} min={0} /></div>
              </div>
              {commodityTotal > 0 && <p className="text-sm text-muted-foreground">Total: {formatINR(commodityTotal)}</p>}
            </>
          )}

          {assetType === "silver" && (
            <>
              <div className="space-y-2">
                <Label>Investment Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !purchaseDate && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {purchaseDate ? format(purchaseDate, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={purchaseDate} onSelect={(d) => d && setPurchaseDate(d)} initialFocus className="p-3 pointer-events-auto" />
                  </PopoverContent>
                </Popover>
                {isAfter(startOfDay(purchaseDate), startOfDay(new Date())) && (
                  <p className="text-destructive text-xs">Investment date cannot be in the future</p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2"><Label>Weight (grams)</Label><Input type="number" value={weight} onChange={(e) => setWeight(e.target.value ? Number(e.target.value) : "")} min={0} /></div>
                <div className="space-y-2"><Label>Price per Gram (₹)</Label><Input type="number" value={pricePerGram} onChange={(e) => setPricePerGram(e.target.value ? Number(e.target.value) : "")} min={0} /></div>
              </div>
              {commodityTotal > 0 && <p className="text-sm text-muted-foreground">Total: {formatINR(commodityTotal)}</p>}
            </>
          )}

          {assetType === "cash" && (
            <>
              <div className="space-y-2"><Label>Deposit Name</Label><Input value={depositName} onChange={(e) => setDepositName(e.target.value)} placeholder="e.g. SBI Fixed Deposit" required /></div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2"><Label>Deposit Amount (₹)</Label><Input type="number" value={depositAmount} onChange={(e) => setDepositAmount(e.target.value ? Number(e.target.value) : "")} min={0} /></div>
                <div className="space-y-2"><Label>Interest Rate (%)</Label><Input type="number" value={interestRate} onChange={(e) => setInterestRate(e.target.value ? Number(e.target.value) : "")} min={0} max={100} step={0.01} /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2"><Label>Term (months)</Label><Input type="number" value={termMonths} onChange={(e) => setTermMonths(e.target.value ? Number(e.target.value) : "")} min={1} /></div>
                <div className="space-y-2">
                  <Label>Interest Type</Label>
                  <Select value={interestType} onValueChange={setInterestType}>
                    <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Compound Interest">Compound Interest</SelectItem>
                      <SelectItem value="Simple Interest">Simple Interest</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Investment Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !purchaseDate && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {purchaseDate ? format(purchaseDate, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={purchaseDate} onSelect={(d) => d && setPurchaseDate(d)} initialFocus className="p-3 pointer-events-auto" />
                  </PopoverContent>
                </Popover>
                {isAfter(startOfDay(purchaseDate), startOfDay(new Date())) && (
                  <p className="text-destructive text-xs">Investment date cannot be in the future</p>
                )}
              </div>
              {maturityDate && <p className="text-sm text-muted-foreground">Maturity Date: {format(maturityDate, "PPP")}</p>}
            </>
          )}

          {assetType && assetType !== "commodities" && (
            <Button onClick={handleSubmit} className="w-full" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Add Asset
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AddAssetModal;
