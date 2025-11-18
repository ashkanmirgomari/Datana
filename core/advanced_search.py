import re
from core.database import load_records
from datetime import datetime

class AdvancedSearch:
    @staticmethod
    def regex_search(pattern, field='all'):

        records = load_records()
        results = []
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return []
        
        for record in records:
            if field == 'all':
                text_to_search = f"{record.get('first_name', '')} {record.get('last_name', '')} {record.get('address', '')} {record.get('national_id', '')} {record.get('phone', '')}"
                if regex.search(text_to_search):
                    results.append(record)
            elif field in record:
                if record[field] and regex.search(str(record[field])):
                    results.append(record)
        
        return results
    
    @staticmethod
    def date_search(date_filter, field='created_at'):
        records = load_records()
        results = []
        
        try:
            target_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        except ValueError:
            return []
        
        for record in records:
            if field in record and record[field]:
                try:
                    record_date = datetime.strptime(record[field][:10], '%Y-%m-%d').date()
                    if record_date == target_date:
                        results.append(record)
                except ValueError:
                    continue
        
        return results
    
    @staticmethod
    def empty_field_search(field):
        records = load_records()
        results = []
        
        for record in records:
            if not record.get(field):
                results.append(record)
        
        return results
    
    @staticmethod
    def range_search(field, min_val=None, max_val=None):
        records = load_records()
        results = []
        
        for record in records:
            value = record.get(field)
            if value and value.isdigit():
                num_value = int(value)
                if (min_val is None or num_value >= min_val) and (max_val is None or num_value <= max_val):
                    results.append(record)
        
        return results
    
    @staticmethod
    def complex_search(filters):
        records = load_records()
        results = []
        
        for record in records:
            match = True
            
            for field, condition in filters.items():
                if not AdvancedSearch._check_condition(record, field, condition):
                    match = False
                    break
            
            if match:
                results.append(record)
        
        return results
    
    @staticmethod
    def _check_condition(record, field, condition):
        value = record.get(field, '')
        
        if condition.get('type') == 'regex':
            try:
                regex = re.compile(condition['pattern'], re.IGNORECASE)
                return bool(regex.search(str(value)))
            except re.error:
                return False
        
        elif condition.get('type') == 'empty':
            return not value
        
        elif condition.get('type') == 'equals':
            return str(value) == condition['value']
        
        elif condition.get('type') == 'contains':
            return condition['value'].lower() in str(value).lower()
        
        return False