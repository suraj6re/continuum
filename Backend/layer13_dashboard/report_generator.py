from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from datetime import datetime

class ReportGenerator:
    """
    Structured PDF Report Generator - Compliance-grade document
    
    Principles:
    - Deterministic output
    - Structured sections
    - Pulls only approved data
    - Compliance markers
    - Audit-ready
    """
    
    def __init__(self, dashboard_data):
        self.data = dashboard_data
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30
        ))
    
    def generate_pdf(self, file_path: str):
        """
        Generate complete PDF report
        
        Args:
            file_path: Output PDF file path
        """
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []
        
        # Build all sections
        elements += self._title_page()
        elements.append(PageBreak())
        elements += self._project_overview()
        elements += self._qto_section()
        elements += self._cost_section()
        elements += self._schedule_section()
        elements += self._risk_section()
        elements += self._compliance_section()
        
        # Build PDF
        doc.build(elements)
    
    def _title_page(self):
        """Generate title page"""
        elements = []
        elements.append(Spacer(1, 2 * inch))
        elements.append(Paragraph("PROJECT COMPLIANCE REPORT", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                 self.styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        summary = self.data['summary']
        elements.append(Paragraph(f"Total Items: {summary['total_items']}", self.styles['Normal']))
        elements.append(Paragraph(f"Approved Items: {summary['approved_count']}", self.styles['Normal']))
        elements.append(Paragraph(f"Export Status: {'✓ Ready' if summary['export_ready'] else '✗ Not Ready'}", 
                                 self.styles['Normal']))
        
        return elements
    
    def _project_overview(self):
        """Section 1: Project Overview"""
        elements = []
        elements.append(Paragraph("1. PROJECT OVERVIEW", self.styles['Heading1']))
        elements.append(Spacer(1, 0.3 * inch))
        
        summary = self.data['summary']
        
        overview_data = [
            ['Metric', 'Value'],
            ['Total QTO Items', str(summary['total_items'])],
            ['Approved Items', str(summary['approved_count'])],
            ['Unapproved Items', str(summary['unapproved_count'])],
            ['Export Ready', 'Yes' if summary['export_ready'] else 'No']
        ]
        
        table = Table(overview_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))
        return elements
    
    def _qto_section(self):
        """Section 2: Quantity Take-Off"""
        elements = []
        elements.append(Paragraph("2. QUANTITY TAKE-OFF (QTO)", self.styles['Heading1']))
        elements.append(Spacer(1, 0.3 * inch))
        
        qto_data = [['Item', 'Quantity', 'Unit', 'Status']]
        
        for item, values in self.data['qto'].items():
            qto_data.append([
                item,
                str(values.get('quantity', 'N/A')),
                values.get('unit', 'N/A'),
                values.get('status', 'N/A')
            ])
        
        table = Table(qto_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))
        return elements
    
    def _cost_section(self):
        """Section 3: Cost Breakdown"""
        elements = []
        elements.append(Paragraph("3. COST BREAKDOWN", self.styles['Heading1']))
        elements.append(Spacer(1, 0.3 * inch))
        
        cost = self.data['cost']
        
        # Total cost
        elements.append(Paragraph(f"<b>Total Project Cost:</b> ₹{cost.get('total_cost', 0):,}", 
                                 self.styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Item-wise breakdown
        if 'item_wise' in cost and cost['item_wise']:
            elements.append(Paragraph("<b>Item-wise Cost:</b>", self.styles['Heading2']))
            elements.append(Spacer(1, 0.1 * inch))
            
            cost_data = [['Item', 'Cost (₹)']]
            for item, amount in cost['item_wise'].items():
                cost_data.append([item, f"₹{amount:,}"])
            
            table = Table(cost_data, colWidths=[4*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        elements.append(Spacer(1, 0.5 * inch))
        return elements
    
    def _schedule_section(self):
        """Section 4: Schedule Summary"""
        elements = []
        elements.append(Paragraph("4. SCHEDULE SUMMARY", self.styles['Heading1']))
        elements.append(Spacer(1, 0.3 * inch))
        
        schedule = self.data['schedule']
        
        elements.append(Paragraph(f"<b>Total Duration:</b> {schedule.get('total_duration', 0)} days", 
                                 self.styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Critical path
        if 'critical_path' in schedule and schedule['critical_path']:
            elements.append(Paragraph("<b>Critical Path:</b>", self.styles['Heading2']))
            elements.append(Spacer(1, 0.1 * inch))
            critical_path_text = " → ".join(schedule['critical_path'])
            elements.append(Paragraph(critical_path_text, self.styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Tasks table
        if 'tasks' in schedule and schedule['tasks']:
            elements.append(Paragraph("<b>Task Breakdown:</b>", self.styles['Heading2']))
            elements.append(Spacer(1, 0.1 * inch))
            
            task_data = [['Task', 'Duration (days)', 'Status']]
            for task in schedule['tasks']:
                task_data.append([
                    task.get('name', 'N/A'),
                    str(task.get('duration', 0)),
                    task.get('status', 'N/A').title()
                ])
            
            table = Table(task_data, colWidths=[3*inch, 1.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        elements.append(Spacer(1, 0.5 * inch))
        return elements
    
    def _risk_section(self):
        """Section 5: Risk & Confidence Analysis"""
        elements = []
        elements.append(Paragraph("5. RISK & CONFIDENCE ANALYSIS", self.styles['Heading1']))
        elements.append(Spacer(1, 0.3 * inch))
        
        risk = self.data['risk']
        confidence = self.data['confidence']
        
        risk_data = [
            ['Metric', 'Value'],
            ['High Risk Items', str(risk.get('high_risk_items', 0))],
            ['Confidence Score', str(risk.get('confidence_score', 0))],
            ['Uncertainty', risk.get('uncertainty', 'N/A')],
            ['Average Confidence', str(confidence.get('average', 0))],
            ['Low Confidence Elements', str(confidence.get('low_confidence_elements', 0))]
        ]
        
        table = Table(risk_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))
        return elements
    
    def _compliance_section(self):
        """Section 6: Compliance Statement"""
        elements = []
        elements.append(Paragraph("6. COMPLIANCE STATEMENT", self.styles['Heading1']))
        elements.append(Spacer(1, 0.3 * inch))
        
        export_status = self.data['export_status']
        
        if export_status['can_export']:
            statement = """
            <b>✓ COMPLIANT</b><br/>
            All QTO items have been reviewed and approved. 
            This report meets compliance requirements and is ready for export.
            """
            bg_color = colors.lightgreen
        else:
            statement = f"""
            <b>✗ NON-COMPLIANT</b><br/>
            This report contains unapproved items and does not meet compliance requirements.<br/>
            Reason: {export_status.get('reason', 'Unknown')}
            """
            bg_color = colors.lightcoral
        
        # Compliance box
        compliance_table = Table([[Paragraph(statement, self.styles['Normal'])]], 
                                colWidths=[6.5*inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, colors.black)
        ]))
        
        elements.append(compliance_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Signature section
        elements.append(Spacer(1, 1 * inch))
        elements.append(Paragraph("_" * 50, self.styles['Normal']))
        elements.append(Paragraph("Authorized Signature", self.styles['Normal']))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", 
                                 self.styles['Normal']))
        
        return elements
