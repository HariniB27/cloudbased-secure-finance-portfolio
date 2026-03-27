import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TrendingUp, RefreshCw, Download, LogOut, Loader2 } from "lucide-react";
import { downloadPortfolioReport, refreshPortfolio } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import OverviewTab from "@/components/dashboard/OverviewTab";
import AssetsTab from "@/components/dashboard/AssetsTab";
import RiskAdvisorTab from "@/components/dashboard/RiskAdvisorTab";
import PerformanceTab from "@/components/dashboard/PerformanceTab";

const Dashboard = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshPortfolio();
      setRefreshKey((k) => k + 1);
      toast({ title: "Portfolio refreshed successfully!" });
    } catch {
      toast({ title: "Refresh failed", variant: "destructive" });
    } finally {
      setRefreshing(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const handleDownload = async () => {
    if (downloading) return;
    setDownloading(true);
    const progressToast = toast({ title: "Preparing report..." });
    try {
      const response = await downloadPortfolioReport();
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      const contentDisposition = response.headers["content-disposition"] as string | undefined;
      const match = contentDisposition?.match(/filename="?([^"]+)"?/);
      const filename = match?.[1] || "portfolio_report.pdf";

      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      // Revoke on next tick so browser can start the download reliably.
      setTimeout(() => URL.revokeObjectURL(url), 0);
      progressToast.dismiss();
      toast({ title: "Report downloaded" });
    } catch {
      progressToast.dismiss();
      toast({ title: "Report download failed", variant: "destructive" });
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold text-foreground">Portfolio Manager</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleDownload} disabled={downloading}>
              {downloading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
              <span className="hidden sm:inline">Download Report</span>
            </Button>
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
              {refreshing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              <span className="hidden sm:inline ml-2">Refresh</span>
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        <Tabs defaultValue="overview">
          <TabsList className="mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="assets">Assets Portfolio</TabsTrigger>
            <TabsTrigger value="performance">Performance Metrics</TabsTrigger>
            <TabsTrigger value="risk">Risk & Advisor</TabsTrigger>
          </TabsList>
          <TabsContent value="overview"><OverviewTab refreshKey={refreshKey} /></TabsContent>
          <TabsContent value="assets"><AssetsTab refreshKey={refreshKey} /></TabsContent>
          <TabsContent value="performance"><PerformanceTab refreshKey={refreshKey} /></TabsContent>
          <TabsContent value="risk"><RiskAdvisorTab refreshKey={refreshKey} /></TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Dashboard;
