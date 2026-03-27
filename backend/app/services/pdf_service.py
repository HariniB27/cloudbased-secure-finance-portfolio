from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Tuple
from app.models.asset import Asset, AssetType
from app.schemas.portfolio import PortfolioSummary, RiskPrediction, AdvisorAdvice
import os


class PDFService:
    """Service for generating PDF portfolio reports"""
    
    @staticmethod
    def _ensure_currency_font() -> str:
        """
        Ensure a font that supports the ₹ symbol.
        Falls back to Helvetica if no suitable font is available.
        """
        if "DejaVuSans" in pdfmetrics.getRegisteredFontNames():
            return "DejaVuSans"

        candidate_paths = [
            "/Library/Fonts/DejaVu Sans.ttf",
            "/Library/Fonts/DejaVuSans.ttf",
            "/System/Library/Fonts/Supplemental/DejaVu Sans.ttf",
            "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont("DejaVuSans", p))
                    return "DejaVuSans"
                except Exception:
                    continue
        return "Helvetica"

    @staticmethod
    def _fmt_inr(value: float) -> str:
        try:
            # Use INR text to avoid missing-glyph squares in environments
            # where the rupee symbol font is unavailable.
            return f"INR {float(value):,.2f}"
        except Exception:
            return "INR 0.00"

    @staticmethod
    def _fmt_pct(value: float) -> str:
        try:
            return f"{float(value):.2f}%"
        except Exception:
            return "0.00%"

    @staticmethod
    def _asset_type_label(asset_type: AssetType) -> str:
        labels = {
            AssetType.EQUITY: "Equity",
            AssetType.MUTUAL_FUND: "Debt (Mutual Funds)",
            AssetType.DEBT: "Debt (Mutual Funds)",
            AssetType.GOLD: "Gold",
            AssetType.SILVER: "Silver",
            AssetType.CASH: "Fixed Deposits",
        }
        return labels.get(asset_type, str(asset_type.value))

    @staticmethod
    def _compute_totals(assets: List[Asset]) -> Tuple[float, float, float, float]:
        total_invested = sum(float(a.invested_amount or 0.0) for a in assets)
        total_current = sum(float(a.current_value or 0.0) for a in assets)
        gain_loss = total_current - total_invested
        gain_loss_pct = (gain_loss / total_invested * 100.0) if total_invested else 0.0
        return total_invested, total_current, gain_loss, gain_loss_pct

    @staticmethod
    def _breakdown_by_type(assets: List[Asset]) -> Dict[AssetType, float]:
        totals: Dict[AssetType, float] = {
            AssetType.EQUITY: 0.0,
            AssetType.MUTUAL_FUND: 0.0,
            AssetType.DEBT: 0.0,
            AssetType.GOLD: 0.0,
            AssetType.SILVER: 0.0,
            AssetType.CASH: 0.0,
        }
        for a in assets:
            totals[a.asset_type] = totals.get(a.asset_type, 0.0) + float(a.current_value or 0.0)
        return totals

    @staticmethod
    def generate_portfolio_report(
        assets: List[Asset],
        summary: PortfolioSummary,
        risk: RiskPrediction,
        advice: AdvisorAdvice,
        username: str
    ) -> BytesIO:
        """Generate a professional portfolio PDF report."""

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=0.65 * inch,
            rightMargin=0.65 * inch,
            topMargin=0.7 * inch,
            bottomMargin=0.7 * inch,
        )
        story = []

        styles = getSampleStyleSheet()
        font_name = PDFService._ensure_currency_font()

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontName=font_name,
            fontSize=18,
            textColor=colors.HexColor("#111827"),
            alignment=TA_LEFT,
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor("#6b7280"),
            alignment=TA_LEFT,
            spaceAfter=12,
        )
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=12,
            textColor=colors.HexColor("#111827"),
            spaceBefore=12,
            spaceAfter=8,
        )
        small_style = ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=9,
            textColor=colors.HexColor("#374151"),
        )
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=8,
            textColor=colors.HexColor("#6b7280"),
            alignment=TA_CENTER,
        )

        generated_at = datetime.now()
        total_invested, total_current, gain_loss, gain_loss_pct = PDFService._compute_totals(assets)
        is_profit = gain_loss >= 0
        gl_color = colors.HexColor("#16a34a") if is_profit else colors.HexColor("#dc2626")

        # HEADER
        story.append(Paragraph("Portfolio Manager", title_style))
        story.append(Paragraph("Portfolio Summary Report", ParagraphStyle("Rpt", parent=title_style, fontSize=16)))
        story.append(
            Paragraph(
                f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M')}   •   User: {username}",
                subtitle_style,
            )
        )

        # SUMMARY CARDS (as a styled table)
        summary_cards = [
            ["Total Invested", PDFService._fmt_inr(total_invested), "Current Value", PDFService._fmt_inr(total_current)],
            ["Total Gain/Loss", PDFService._fmt_inr(gain_loss), "Gain/Loss (%)", PDFService._fmt_pct(gain_loss_pct)],
        ]
        cards = Table(summary_cards, colWidths=[1.6 * inch, 2.0 * inch, 1.4 * inch, 2.0 * inch])
        cards.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                    ("TEXTCOLOR", (1, 1), (1, 1), gl_color),
                    ("TEXTCOLOR", (3, 1), (3, 1), gl_color),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(cards)
        story.append(Spacer(1, 0.2 * inch))

        # ASSET ALLOCATION TABLE (asset-wise)
        story.append(Paragraph("Asset Allocation (Holdings)", section_style))
        holdings = [[
            "Asset Name",
            "Type",
            "Quantity",
            "Invested Amount",
            "Current Value",
            "Gain/Loss (₹)",
            "Gain/Loss (%)",
        ]]

        for a in assets:
            invested = float(a.invested_amount or 0.0)
            current = float(a.current_value or 0.0)
            gl = current - invested
            gl_pct = (gl / invested * 100.0) if invested else 0.0
            holdings.append([
                (a.name or "")[:28],
                PDFService._asset_type_label(a.asset_type),
                f"{float(a.quantity or 0.0):,.4f}".rstrip("0").rstrip(".") if a.quantity is not None else "—",
                PDFService._fmt_inr(invested),
                PDFService._fmt_inr(current),
                PDFService._fmt_inr(gl),
                PDFService._fmt_pct(gl_pct),
            ])

        col_widths = [1.7 * inch, 1.0 * inch, 0.8 * inch, 1.0 * inch, 1.0 * inch, 0.95 * inch, 0.85 * inch]
        holdings_table = Table(holdings, colWidths=col_widths, repeatRows=1)
        holdings_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                    ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(holdings_table)

        # ASSET TYPE BREAKDOWN
        story.append(Spacer(1, 0.18 * inch))
        story.append(Paragraph("Asset Type Breakdown", section_style))
        by_type = PDFService._breakdown_by_type(assets)
        total_value = sum(by_type.values()) or 1.0
        breakdown_rows = [["Asset Type", "Total Value", "Allocation %"]]
        debt_mf_total = float(by_type.get(AssetType.DEBT, 0.0)) + float(by_type.get(AssetType.MUTUAL_FUND, 0.0))
        breakdown_entries = [
            ("Equity", float(by_type.get(AssetType.EQUITY, 0.0))),
            ("Debt (Mutual Funds)", debt_mf_total),
            ("Gold", float(by_type.get(AssetType.GOLD, 0.0))),
            ("Silver", float(by_type.get(AssetType.SILVER, 0.0))),
            ("Fixed Deposits", float(by_type.get(AssetType.CASH, 0.0))),
        ]
        for label, value in breakdown_entries:
            breakdown_rows.append([label, PDFService._fmt_inr(value), f"{(value/total_value*100):.1f}%"])
        breakdown_rows.append(["Total", PDFService._fmt_inr(total_value), "100.0%"])
        breakdown_table = Table(breakdown_rows, colWidths=[2.3 * inch, 2.1 * inch, 1.6 * inch], repeatRows=1)
        breakdown_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f9fafb")]),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e5e7eb")),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(breakdown_table)

        # ADVISORY SECTION
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Advisory Insights", section_style))

        def _safe_text(value: str) -> str:
            return (value or "N/A").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        story.append(Paragraph("<b>Portfolio Health</b>", small_style))
        story.append(Paragraph(_safe_text(advice.portfolio_health), small_style))
        story.append(Spacer(1, 0.08 * inch))

        story.append(Paragraph("<b>Priority Actions</b>", small_style))
        actions = advice.risk_reduction_actions or []
        if actions:
            for idx, action in enumerate(actions[:5], start=1):
                story.append(Paragraph(f"{idx}. {_safe_text(action)}", small_style))
        else:
            story.append(Paragraph("N/A", small_style))
        story.append(Spacer(1, 0.08 * inch))

        story.append(Paragraph("<b>Diversification Insights</b>", small_style))
        insights = advice.diversification_insights or []
        if insights:
            for idx, insight in enumerate(insights[:5], start=1):
                story.append(Paragraph(f"{idx}. {_safe_text(insight)}", small_style))
        else:
            story.append(Paragraph("N/A", small_style))
        story.append(Spacer(1, 0.08 * inch))

        story.append(Paragraph("<b>Scenario Insights</b>", small_style))
        story.append(Paragraph(_safe_text(advice.scenario_insights), small_style))
        story.append(Spacer(1, 0.08 * inch))

        story.append(Paragraph("<b>Strategy Recommendation</b>", small_style))
        story.append(Paragraph(_safe_text(advice.strategy_recommendation), small_style))

        # FOOTER
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph("Generated by Portfolio Manager • For informational purposes only.", footer_style))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
