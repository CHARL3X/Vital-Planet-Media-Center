"""
Vital Planet Asset Hub - Temporal Analysis
Extract meaningful work activity timestamps from files and directories.
"""

import re
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class TemporalAnalyzer:
    """Analyzes temporal patterns in VP packaging assets for accurate timeline data."""
    
    def __init__(self):
        self.date_patterns = self._compile_date_patterns()
        
    def _compile_date_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """Compile regex patterns for VP-specific date formats."""
        patterns = [
            # VP Art filename patterns: ARTM03Y25, ART03Y25, DRAFT02 241116
            (re.compile(r'ART(?:M)?(\d{2})Y(\d{2})'), 'art_date'),  # ARTM03Y25 = March 2025
            (re.compile(r'DRAFT\d+\s*(\d{2})(\d{2})(\d{2})'), 'draft_date'),  # DRAFT02 241116 = Nov 16, 2024
            
            # Version dates: 08-23, 12.20, etc.
            (re.compile(r'(\d{2})[.-](\d{2})(?:[.-](\d{2,4}))?'), 'version_date'),  # 08-23, 12.20
            
            # ISO-like dates: 2024-03-15, 20240315
            (re.compile(r'(\d{4})[.-](\d{1,2})[.-](\d{1,2})'), 'iso_date'),
            (re.compile(r'(\d{4})(\d{2})(\d{2})'), 'compact_date'),
            
            # Month-year: M03Y25, 032025
            (re.compile(r'M(\d{2})Y(\d{2})'), 'month_year'),
            (re.compile(r'(\d{2})(\d{4})'), 'month_year_full'),
        ]
        return patterns
    
    def extract_filename_dates(self, filename: str) -> List[Dict[str, Any]]:
        """Extract all possible dates from a filename with confidence scores."""
        dates = []
        filename_lower = filename.lower()
        
        for pattern, pattern_type in self.date_patterns:
            matches = pattern.finditer(filename)
            for match in matches:
                parsed_date = self._parse_date_match(match, pattern_type)
                if parsed_date:
                    dates.append({
                        'date': parsed_date,
                        'pattern_type': pattern_type,
                        'match_text': match.group(0),
                        'confidence': self._calculate_confidence(pattern_type, match.group(0), filename_lower),
                        'position': match.start()
                    })
        
        # Sort by confidence (highest first)
        dates.sort(key=lambda x: x['confidence'], reverse=True)
        return dates
    
    def _parse_date_match(self, match: re.Match, pattern_type: str) -> Optional[datetime]:
        """Parse a regex match into a datetime object."""
        try:
            groups = match.groups()
            
            if pattern_type == 'art_date':
                # ARTM03Y25 = March 2025
                month, year = int(groups[0]), 2000 + int(groups[1])
                return datetime(year, month, 1)
                
            elif pattern_type == 'draft_date':
                # DRAFT02 241116 = November 16, 2024
                year, month, day = 2000 + int(groups[0]), int(groups[1]), int(groups[2])
                return datetime(year, month, day)
                
            elif pattern_type == 'version_date':
                # 08-23 could be August 2023 or Month-Day
                month, day_or_year = int(groups[0]), int(groups[1])
                year_part = groups[2] if len(groups) > 2 and groups[2] else None
                
                if year_part:
                    year = int(year_part)
                    if year < 100:
                        year += 2000
                    return datetime(year, month, day_or_year)
                else:
                    # Guess: if second number > 12, it's probably a year
                    if day_or_year > 12:
                        return datetime(2000 + day_or_year, month, 1)
                    else:
                        # Could be month-day, assume current year
                        current_year = datetime.now().year
                        return datetime(current_year, month, day_or_year)
                        
            elif pattern_type in ['iso_date', 'compact_date']:
                year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                return datetime(year, month, day)
                
            elif pattern_type == 'month_year':
                # M03Y25 = March 2025
                month, year = int(groups[0]), 2000 + int(groups[1])
                return datetime(year, month, 1)
                
            elif pattern_type == 'month_year_full':
                # 032025 = March 2025
                month, year = int(groups[0]), int(groups[1])
                return datetime(year, month, 1)
                
        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse date from {match.group(0)}: {e}")
            return None
    
    def _calculate_confidence(self, pattern_type: str, match_text: str, filename: str) -> float:
        """Calculate confidence score for a date extraction - filename dates are project versions, not work activity."""
        # Lower base confidence since filename dates are project versions, not work timestamps
        base_confidence = {
            'art_date': 0.4,        # ARTM03Y25 is project version, not work date
            'draft_date': 0.5,      # DRAFT patterns show iteration, not work timing
            'version_date': 0.3,    # Version numbers, not activity dates
            'iso_date': 0.4,        # Could be versions or actual dates
            'compact_date': 0.3,    # Likely version numbers
            'month_year': 0.4,      # Project timeline, not work activity
            'month_year_full': 0.3  # Could be anything
        }.get(pattern_type, 0.2)
        
        # Small boosts for context, but keep expectations low
        if 'draft' in filename:
            base_confidence += 0.1  # Drafts might indicate recent iteration
        if 'final' in filename or 'print ready' in filename.lower():
            base_confidence += 0.05  # Completion markers
            
        return min(base_confidence, 0.6)  # Cap at 0.6 - filename dates aren't primary indicators
    
    def get_best_project_date(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get the most reliable project date from a filename."""
        dates = self.extract_filename_dates(filename)
        if dates:
            return dates[0]  # Highest confidence
        return None
    
    def analyze_file_activity(self, file_path: Path) -> Dict[str, Any]:
        """Comprehensive analysis of a file's temporal signatures."""
        try:
            stat = file_path.stat()
            
            # Basic file system timestamps
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            created_time = datetime.fromtimestamp(stat.st_ctime)
            accessed_time = datetime.fromtimestamp(stat.st_atime)
            
            # Extract filename dates
            filename_dates = self.extract_filename_dates(file_path.name)
            best_project_date = self.get_best_project_date(file_path.name)
            
            # Analyze modification patterns
            activity_score = self._calculate_activity_score(stat, filename_dates, modified_time, file_path)
            
            return {
                'file_path': str(file_path),
                'filesystem_dates': {
                    'modified': modified_time.isoformat(),
                    'created': created_time.isoformat(),
                    'accessed': accessed_time.isoformat()
                },
                'filename_dates': [
                    {
                        'date': d['date'].isoformat(),
                        'pattern_type': d['pattern_type'],
                        'match_text': d['match_text'],
                        'confidence': d['confidence']
                    } for d in filename_dates
                ],
                'best_project_date': {
                    'date': best_project_date['date'].isoformat(),
                    'pattern_type': best_project_date['pattern_type'],
                    'match_text': best_project_date['match_text'],
                    'confidence': best_project_date['confidence']
                } if best_project_date else None,
                'activity_score': activity_score,
                'file_size': stat.st_size,
                'is_recent_work': self._is_recent_work(modified_time, best_project_date, stat.st_size)
            }
            
        except (OSError, ValueError) as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {'error': str(e)}
    
    def _calculate_activity_score(self, stat: os.stat_result, filename_dates: List[Dict], modified_time: datetime, file_path: Path) -> float:
        """Calculate how likely this represents real work activity - prioritize file system data over filename dates."""
        score = 0.0
        
        # FILE SIZE - Primary indicator of meaningful work
        if stat.st_size > 50 * 1024 * 1024:  # >50MB = major work file
            score += 0.4
        elif stat.st_size > 10 * 1024 * 1024:  # >10MB = substantial work
            score += 0.3
        elif stat.st_size > 1024 * 1024:  # >1MB = some work
            score += 0.2
        elif stat.st_size > 100 * 1024:  # >100KB = minor work
            score += 0.1
            
        # RECENT MODIFICATIONS - Strong indicator of current work
        days_since_modified = (datetime.now() - modified_time).days
        if days_since_modified < 3:  # Very recent
            score += 0.4
        elif days_since_modified < 7:  # This week
            score += 0.3
        elif days_since_modified < 30:  # This month
            score += 0.2
        elif days_since_modified < 90:  # This quarter
            score += 0.1
            
        # FILE TYPE - Work files vs exports
        ext = file_path.suffix.lower()
        if ext in ['.psd', '.ai', '.indd']:  # Source work files
            score += 0.3
        elif ext in ['.pdf']:  # Final outputs
            score += 0.2
        elif ext in ['.png', '.jpg', '.jpeg']:  # Could be exports or work
            score += 0.1
            
        # DIRECTORY CONTEXT - Where the file lives matters
        path_str = str(file_path).lower()
        if 'print ready' in path_str or 'final' in path_str:
            score += 0.2  # Recent completion work
        elif 'draft' in path_str or 'work in progress' in path_str:
            score += 0.15  # Active development
        elif 'old' in path_str or 'archive' in path_str or 'backup' in path_str:
            score *= 0.5  # Reduce score for archived content
            
        # FILENAME DATES - Minor factor (since you noted they're not that useful)
        if filename_dates:
            score += 0.05 * filename_dates[0]['confidence']  # Very small boost
            
        return min(score, 1.0)
    
    def _is_recent_work(self, modified_time: datetime, project_date: Optional[Dict], file_size: int) -> bool:
        """Determine if this represents recent meaningful work - focus on file system activity."""
        days_since_modified = (datetime.now() - modified_time).days
        
        # Primary indicators: Large files modified recently
        if file_size > 10 * 1024 * 1024 and days_since_modified < 7:  # >10MB, modified this week
            return True
        if file_size > 1024 * 1024 and days_since_modified < 3:  # >1MB, modified in last 3 days
            return True
            
        # Secondary indicator: Any significant file modified very recently
        if file_size > 100 * 1024 and days_since_modified < 1:  # >100KB, modified today
            return True
            
        # Filename dates are less reliable, so much lower threshold
        if project_date and project_date['confidence'] > 0.5:
            try:
                project_datetime = datetime.fromisoformat(project_date['date'].replace('Z', '+00:00'))
                # Only consider if filename date is recent AND file was modified recently
                if ((datetime.now() - project_datetime).days < 30 and 
                    days_since_modified < 14 and 
                    file_size > 500 * 1024):  # Conservative: filename recent + file modified + substantial size
                    return True
            except (ValueError, KeyError):
                pass
                
        return False
    
    def analyze_directory_timeline(self, directory: Path) -> Dict[str, Any]:
        """Analyze timeline patterns for an entire product directory."""
        files_analysis = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                analysis = self.analyze_file_activity(file_path)
                if 'error' not in analysis:
                    files_analysis.append(analysis)
        
        if not files_analysis:
            return {'error': 'No files found or analyzed'}
        
        # Find the most meaningful project timeline
        project_dates = [f['best_project_date'] for f in files_analysis if f['best_project_date']]
        recent_work = [f for f in files_analysis if f['is_recent_work']]
        
        # Sort by confidence and recency
        if project_dates:
            best_project_dates = sorted(project_dates, 
                                      key=lambda x: (x['confidence'], x['date']), 
                                      reverse=True)
        else:
            best_project_dates = []
        
        return {
            'directory': str(directory),
            'total_files': len(files_analysis),
            'recent_work_files': len(recent_work),
            'best_project_dates': best_project_dates[:5],  # Top 5 most confident dates
            'latest_activity': max(f['filesystem_dates']['modified'] for f in files_analysis),
            'earliest_project_date': min(p['date'] for p in project_dates) if project_dates else None,
            'activity_summary': {
                'high_activity': len([f for f in files_analysis if f['activity_score'] > 0.7]),
                'medium_activity': len([f for f in files_analysis if 0.3 < f['activity_score'] <= 0.7]),
                'low_activity': len([f for f in files_analysis if f['activity_score'] <= 0.3])
            }
        }

def test_temporal_analyzer():
    """Test the temporal analyzer with VP filename patterns."""
    analyzer = TemporalAnalyzer()
    
    test_files = [
        "19003-L-Vital Flora FG Women's Daily 30ct Packaging-ART03Y25.ai",
        "19003-B-Vital Flora FG Women's Daily 30ct Packaging-ARTM11Y24.ai",
        "19003-L-Vital Flora FG Women's Daily 30ct Packaging-DRAFT02 241116.ai",
        "19002 VF FG ULTRA DAILY 30ct 08-23.psd",
        "Critical Liver Care Box 12.20.psd"
    ]
    
    for filename in test_files:
        print(f"\n--- {filename} ---")
        dates = analyzer.extract_filename_dates(filename)
        for date_info in dates:
            print(f"Date: {date_info['date']}, Pattern: {date_info['pattern_type']}, "
                  f"Confidence: {date_info['confidence']:.2f}, Match: {date_info['match_text']}")

if __name__ == "__main__":
    test_temporal_analyzer()