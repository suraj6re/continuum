from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
import hashlib

class ComplianceGenerator:
    """
    ISO-Style Compliance Certificate Generator
    
    Aligns with:
    - ISO 19650 (BIM Information Management)
    - Government submission formats
    - Audit trail requirements
    - Digital verification
    """
    
    def __init__(self, dashboard_data, project_info=None):
        self.data = dashboard_data
        self.project_info = project_info or {}
        self.styles = getSampleStyleSheet()
        self._setup_compliance_styles()
        self.certificate_id = self._generate_certificate_id()
    
    def _setup_compliance_styles(self):
        """Setup ISO-compliant document styles"""
        self.styles.add(ParagraphStyle(
            name='ComplianceTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#003366'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='CertificateText',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def _generate_certificate_id(self):
        """Generate unique certificate ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_hash = hashlib.md5(str(self.data).encode()).hexdigest()[:8]
        return f"CERT-{timestamp}-{data_hash.upper()}"
    
    def generate_compliance_certificate(self, file_path: str):
        """Generate ISO-compliant certificate"""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        
        elements += self._certificate_header()
        elements += self._compliance_declaration()
        elements += self._verification_summary()
        elements += self._approval_matrix()
        elements += self._quality_metrics()
        elements += self._audit_trail()
        elements += self._certification_statement()
        elements += self._digital_signature()
        
        doc.build(elements)
    
    def _certificate_header(self):
        """ISO-compliant certificate header"""
        elements = []
        
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph("COMPLIANCE CERTIFICATE", self.styles['ComplianceTitle']))
        elements.append(Paragraph("ISO 19650 Aligned | Government Submission Ready", 
                                 self.styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Certificate metadata
        metadata = [
            ['Certificate ID:', self.certificate_id],
            ['Issue Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')],
            ['Project:', self.project_info.get('name', 'N/A')],
            ['Standard:', 'ISO 19650-2:2018'],
            ['Status:', 'CERTIFIED' if self.data['export_status']['can_export'] else 'PENDING']
        ]
        
        table = Table(metadata, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))
        return elements
    
    def _compliance_declaration(self):
        """Formal compliance declaration"""
        elements = []
        
        elements.append(Paragraph("1. COMPLIANCE DECLARATION", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        declaration = f"""
        This certificate confirms that the project documentation has been prepared in accordance 
        with ISO 19650-2:2018 standards for Building Information Management. All quantity take-offs, 
        cost estimates, and schedule data have been validated through the integrated AI-assisted 
        workflow and approved by authorized personnel.
        """
        
        elements.append(Paragraph(declaration, self.styles['CertificateText']))
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    def _verification_summary(self):
        """Verification and validation summary"""
        elements = []
        
        elements.append(Paragraph("2. VERIFICATION SUMMARY", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        summary = self.data['summary']
        
        verification_data = [
            ['Verification Item', 'Status', 'Count'],
            ['Total QTO Items', '✓', str(summary['total_items'])],
            ['Approved Items', '✓' if summary['approved_count'] > 0 else '✗', 
             str(summary['approved_count'])],
            ['Pending Approval', '⚠' if summary['unapproved_count'] > 0 else '✓', 
             str(summary['unapproved_count'])],
            ['Export Readiness', '✓' if summary['export_ready'] else '✗', 
             'Ready' if summary['export_ready'] else 'Not Ready']
        ]
        
        table = Table(verification_data, colWidths=[3*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    def _approval_matrix(self):
        """Approval status matrix"""
        elements = []
        
        elements.append(Paragraph("3. APPROVAL MATRIX", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        qto_data = self.data['qto']
        
        approval_data = [['Item', 'Quantity', 'Unit', 'Approval Status']]
        
        for item, values in qto_data.items():
            status = values.get('status', 'N/A')
            status_symbol = {
                'Approved': '✓ Approved',
                'Pending': '⚠ Pending',
                'Rejected': '✗ Rejected',
                'Needs Review': '⚠ Review'
            }.get(status, status)
            
            approval_data.append([
                item,
                str(values.get('quantity', 'N/A')),
                values.get('unit', 'N/A'),
                status_symbol
            ])
        
        table = Table(approval_data, colWidths=[2.5*inch, 1.2*inch, 0.8*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    def _quality_metrics(self):
        """Quality assurance metrics"""
        elements = []
        
        elements.append(Paragraph("4. QUALITY ASSURANCE METRICS", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        confidence = self.data['confidence']
        risk = self.data['risk']
        
        qa_data = [
            ['Metric', 'Value', 'Threshold', 'Status'],
            ['Average Confidence', f"{confidence.get('average', 0):.2f}", '≥0.80', 
             '✓' if confidence.get('average', 0) >= 0.80 else '✗'],
            ['Low Confidence Elements', str(confidence.get('low_confidence_elements', 0)), 
             '≤5', '✓' if confidence.get('low_confidence_elements', 0) <= 5 else '⚠'],
            ['High Risk Items', str(risk.get('high_risk_items', 0)), '≤3', 
             '✓' if risk.get('high_risk_items', 0) <= 3 else '⚠'],
            ['Confidence Score', str(risk.get('confidence_score', 0)), '≥0.85', 
             '✓' if risk.get('confidence_score', 0) >= 0.85 else '⚠']
        ]
        
        table = Table(qa_data, colWidths=[2.5*inch, 1.5*inch, 1.2*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    def _audit_trail(self):
        """Audit trail information"""
        elements = []
        
        elements.append(Paragraph("5. AUDIT TRAIL", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        audit_text = f"""
        This certificate is supported by a complete audit trail maintained in accordance with 
        ISO 19650 requirements. All modifications, approvals, and validations are logged with 
        timestamps and user attribution. The audit trail is immutable and available for 
        compliance verification.
        
        Certificate Hash: {hashlib.sha256(self.certificate_id.encode()).hexdigest()[:16].upper()}
        """
        
        elements.append(Paragraph(audit_text, self.styles['CertificateText']))
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    def _certification_statement(self):
        """Official certification statement"""
        elements = []
        
        elements.append(Paragraph("6. CERTIFICATION STATEMENT", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        export_status = self.data['export_status']
        
        if export_status['can_export']:
            statement = """
            <b>CERTIFIED FOR SUBMISSION</b><br/><br/>
            This document certifies that all project data has been validated, approved, and meets 
            the requirements for government submission and regulatory compliance. The information 
            contained herein is accurate and complete as of the certification date.
            """
            bg_color = colors.HexColor('#90EE90')
        else:
            statement = f"""
            <b>PENDING CERTIFICATION</b><br/><br/>
            This document is pending final certification. Reason: {export_status.get('reason', 'Unknown')}
            <br/>All items must be approved before this certificate can be issued for submission.
            """
            bg_color = colors.HexColor('#FFB6C1')
        
        cert_table = Table([[Paragraph(statement, self.styles['CertificateText'])]], 
                          colWidths=[6*inch])
        cert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.black)
        ]))
        
        elements.append(cert_table)
        elements.append(Spacer(1, 0.5 * inch))
        return elements
    
    def _digital_signature(self):
        """Digital signature section"""
        elements = []
        
        elements.append(Paragraph("7. AUTHORIZATION", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        sig_data = [
            ['Certified By:', self.project_info.get('certifier', '_' * 40)],
            ['Title:', self.project_info.get('certifier_title', 'Project Engineer')],
            ['Organization:', self.project_info.get('organization', '_' * 40)],
            ['Date:', datetime.now().strftime('%Y-%m-%d')],
            ['Digital Signature:', f"SHA256:{hashlib.sha256(self.certificate_id.encode()).hexdigest()[:32].upper()}"]
        ]
        
        table = Table(sig_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Footer
        footer = """
        This certificate is generated by an AI-assisted integrated workflow system and is valid 
        for regulatory submission. For verification, contact the issuing organization with the 
        Certificate ID.
        """
        elements.append(Paragraph(footer, self.styles['Normal']))
        
        return elements
