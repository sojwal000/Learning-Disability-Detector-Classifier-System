"""
PDF Report Generator for Student Progress Reports
Uses ReportLab to generate comprehensive PDF reports with charts and analytics
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime
import io
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend


class ProgressReportGenerator:
    """Generate comprehensive progress reports in PDF format"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280')
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(
        self,
        student_data: Dict,
        progress_data: Dict,
        comparison_data: Dict,
        heatmap_data: Dict,
        timeline_data: Dict,
        output_path: str
    ) -> str:
        """
        Generate a comprehensive PDF report
        
        Args:
            student_data: Basic student information
            progress_data: Progress over time data
            comparison_data: Grade comparison data
            heatmap_data: Performance heatmap data
            timeline_data: Assessment timeline data
            output_path: Path to save the PDF
            
        Returns:
            Path to the generated PDF file
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title Page
        story.extend(self._create_title_page(student_data))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(progress_data, comparison_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Progress Over Time Chart
        story.extend(self._create_progress_chart(progress_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Comparison with Grade Average
        story.extend(self._create_comparison_section(comparison_data))
        story.append(PageBreak())
        
        # Performance Heatmap
        story.extend(self._create_heatmap_section(heatmap_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Assessment Timeline
        story.extend(self._create_timeline_section(timeline_data))
        
        # Recommendations
        story.extend(self._create_recommendations(progress_data, heatmap_data))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _create_title_page(self, student_data: Dict) -> List:
        """Create the title page"""
        elements = []
        
        # Title
        title = Paragraph(
            "Student Progress Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Student Info Table
        info_data = [
            ['Student Name:', f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}"],
            ['Age:', str(student_data.get('age', 'N/A'))],
            ['Grade:', str(student_data.get('grade', 'N/A'))],
            ['Gender:', student_data.get('gender', 'N/A')],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(info_table)
        return elements
    
    def _create_executive_summary(self, progress_data: Dict, comparison_data: Dict) -> List:
        """Create executive summary section"""
        elements = []
        
        header = Paragraph("Executive Summary", self.styles['SectionHeader'])
        elements.append(header)
        
        stats = progress_data.get('overall_statistics', {})
        
        # Summary metrics table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Tests Taken', str(stats.get('total_tests', 0))],
            ['Average Score', f"{stats.get('average_score', 0):.1f}%"],
            ['Improvement Rate', f"{stats.get('improvement_rate', 0):.1f}%"],
            ['Trend', stats.get('trend', 'stable').upper()],
            ['Best Test Type', stats.get('best_test_type', 'N/A').replace('_', ' ').upper()],
            ['Grade Percentile', f"{comparison_data.get('overall_percentile', 0):.1f}th"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        elements.append(summary_table)
        return elements
    
    def _create_progress_chart(self, progress_data: Dict) -> List:
        """Create progress over time chart using matplotlib"""
        elements = []
        
        header = Paragraph("Progress Over Time", self.styles['SectionHeader'])
        elements.append(header)
        
        progress_over_time = progress_data.get('progress_over_time', [])
        
        if progress_over_time:
            # Group by test type
            test_types = {}
            for entry in progress_over_time:
                test_type = entry['test_type']
                if test_type not in test_types:
                    test_types[test_type] = {'dates': [], 'scores': []}
                test_types[test_type]['dates'].append(datetime.fromisoformat(entry['test_date']))
                test_types[test_type]['scores'].append(entry['avg_score'])
            
            # Create matplotlib chart
            fig, ax = plt.subplots(figsize=(8, 4))
            
            for test_type, data in test_types.items():
                ax.plot(data['dates'], data['scores'], marker='o', label=test_type.replace('_', ' ').title())
            
            ax.set_xlabel('Date')
            ax.set_ylabel('Score (%)')
            ax.set_title('Test Scores Over Time')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)
            
            # Save to buffer
            img_buffer = io.BytesIO()
            plt.tight_layout()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            img_buffer.seek(0)
            
            # Add to PDF
            img = Image(img_buffer, width=6*inch, height=3*inch)
            elements.append(img)
        else:
            elements.append(Paragraph("No progress data available.", self.styles['Normal']))
        
        return elements
    
    def _create_comparison_section(self, comparison_data: Dict) -> List:
        """Create comparison with grade average section"""
        elements = []
        
        header = Paragraph("Performance vs Grade Average", self.styles['SectionHeader'])
        elements.append(header)
        
        test_types = comparison_data.get('test_types', [])
        
        if test_types:
            # Create comparison chart
            fig, ax = plt.subplots(figsize=(8, 4))
            
            labels = [t['test_type'].replace('_', ' ').title() for t in test_types]
            student_scores = [t['student_avg'] for t in test_types]
            grade_scores = [t['grade_avg'] for t in test_types]
            
            x = range(len(labels))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], student_scores, width, label='Student', color='#3b82f6')
            ax.bar([i + width/2 for i in x], grade_scores, width, label='Grade Average', color='#9ca3af')
            
            ax.set_ylabel('Score (%)')
            ax.set_title('Student vs Grade Average')
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_ylim(0, 100)
            
            # Save to buffer
            img_buffer = io.BytesIO()
            plt.tight_layout()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            img_buffer.seek(0)
            
            # Add to PDF
            img = Image(img_buffer, width=6*inch, height=3*inch)
            elements.append(img)
            
            # Add summary text
            summary_text = f"""
            <b>Overall Performance:</b> Student average: {comparison_data.get('student_overall_avg', 0):.1f}%, 
            Grade average: {comparison_data.get('grade_overall_avg', 0):.1f}%<br/>
            <b>Percentile:</b> {comparison_data.get('overall_percentile', 0):.1f}th percentile
            """
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(summary_text, self.styles['Normal']))
        
        return elements
    
    def _create_heatmap_section(self, heatmap_data: Dict) -> List:
        """Create performance heatmap section"""
        elements = []
        
        header = Paragraph("Performance Heatmap", self.styles['SectionHeader'])
        elements.append(header)
        
        dimensions = heatmap_data.get('dimensions', [])
        
        if dimensions:
            # Create table for heatmap
            heatmap_table_data = [['Dimension', 'Score', 'Test Count', 'Performance']]
            
            for dim in dimensions:
                score = dim['score']
                performance = '🟢 Strong' if score >= 70 else '🟡 Moderate' if score >= 40 else '🔴 Needs Work'
                heatmap_table_data.append([
                    dim['dimension'],
                    f"{score:.1f}%",
                    str(dim['test_count']),
                    performance
                ])
            
            heatmap_table = Table(heatmap_table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            heatmap_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
            ]))
            
            elements.append(heatmap_table)
        
        return elements
    
    def _create_timeline_section(self, timeline_data: Dict) -> List:
        """Create assessment timeline section"""
        elements = []
        
        header = Paragraph("Recent Assessment Timeline", self.styles['SectionHeader'])
        elements.append(header)
        
        timeline = timeline_data.get('timeline', [])[:10]  # Last 10 assessments
        
        if timeline:
            timeline_table_data = [['Date', 'Test Type', 'Score', 'ML Prediction']]
            
            for event in timeline:
                date = datetime.fromisoformat(event['test_date']).strftime('%m/%d/%Y')
                test_type = event['test_type'].replace('_', ' ').title()
                score = f"{event['score']:.1f}%"
                ml_pred = f"{event.get('ml_prediction', 0):.1f}%" if event.get('ml_prediction') else 'N/A'
                
                timeline_table_data.append([date, test_type, score, ml_pred])
            
            timeline_table = Table(timeline_table_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
            ]))
            
            elements.append(timeline_table)
        
        return elements
    
    def _create_recommendations(self, progress_data: Dict, heatmap_data: Dict) -> List:
        """Create recommendations section"""
        elements = []
        
        elements.append(PageBreak())
        header = Paragraph("Recommendations", self.styles['SectionHeader'])
        elements.append(header)
        
        stats = progress_data.get('overall_statistics', {})
        trend = stats.get('trend', 'stable')
        dimensions = heatmap_data.get('dimensions', [])
        
        recommendations = []
        
        # Trend-based recommendations
        if trend == 'declining':
            recommendations.append(
                "• <b>Immediate Attention Required:</b> Student shows declining performance. "
                "Consider one-on-one intervention sessions."
            )
        elif trend == 'improving':
            recommendations.append(
                "• <b>Positive Progress:</b> Student is improving. Continue current strategies "
                "and consider advancing difficulty level."
            )
        else:
            recommendations.append(
                "• <b>Stable Performance:</b> Consider introducing new challenges to promote growth."
            )
        
        # Dimension-based recommendations
        weak_areas = [d for d in dimensions if d['score'] < 60]
        if weak_areas:
            recommendations.append(
                f"• <b>Focus Areas:</b> Concentrate on {', '.join([d['dimension'] for d in weak_areas[:3]])}. "
                "These areas need additional support."
            )
        
        # General recommendations
        recommendations.extend([
            "• <b>Regular Assessment:</b> Continue with regular assessments to track progress.",
            "• <b>Parental Involvement:</b> Share progress with parents and discuss strategies for home support.",
            "• <b>Multi-modal Learning:</b> Incorporate visual, auditory, and kinesthetic learning approaches."
        ])
        
        for rec in recommendations:
            elements.append(Paragraph(rec, self.styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
