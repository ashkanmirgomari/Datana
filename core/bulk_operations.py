# core/bulk_operations.py
import re
from datetime import datetime
from core.database import load_records, save_records, delete_record_by_id
from core.logger import log
from core.validators import DataValidator

class BulkOperations:
    
    @staticmethod
    def delete_by_condition(condition, value, dry_run=False):
        """
        حذف گروهی بر اساس شرط
        مثال: delete_by_condition('city', 'tehran')
        """
        records = load_records()
        to_delete = []
        kept = []
        
        for record in records:
            match = False
            if condition == 'city':
                if record.get('address', '').lower() == value.lower():
                    match = True
            elif condition == 'older_than':
                try:
                    cutoff = datetime.strptime(value, '%Y-%m-%d')
                    created = record.get('created_at', '')
                    if created:
                        record_date = datetime.strptime(created[:10], '%Y-%m-%d')
                        if record_date < cutoff:
                            match = True
                except:
                    pass
            elif condition == 'national_id':
                if record.get('national_id') == value:
                    match = True
            elif condition == 'phone':
                if record.get('phone') == value:
                    match = True
            elif condition == 'empty_field':
                if not record.get(value):
                    match = True
            
            if match:
                to_delete.append(record)
            else:
                kept.append(record)
        
        if dry_run:
            return {
                'matched': len(to_delete),
                'records': to_delete
            }
        
        save_records(kept)
        log(f"BULK_DELETE: deleted {len(to_delete)} records by {condition}={value}")
        return len(to_delete)
    
    @staticmethod
    def update_by_condition(condition_field, condition_value, updates, dry_run=False):
        """
        بروزرسانی گروهی
        مثال: update_by_condition('city', 'tehran', {'city': 'karaj', 'add_tag': 'moved'})
        """
        records = load_records()
        updated = []
        unchanged = []
        
        for record in records:
            match = False
            
            # بررسی شرط
            if condition_field == 'city':
                if record.get('address', '').lower() == condition_value.lower():
                    match = True
            elif condition_field == 'national_id':
                if record.get('national_id') == condition_value:
                    match = True
            elif condition_field == 'phone':
                if record.get('phone') == condition_value:
                    match = True
            elif condition_field == 'all':
                match = True
            
            if match:
                # اعمال بروزرسانی‌ها
                for key, value in updates.items():
                    if key == 'city':
                        record['address'] = value
                    elif key == 'add_tag':
                        current_tags = record.get('tags', '')
                        if value not in current_tags:
                            if current_tags:
                                record['tags'] = f"{current_tags},{value}"
                            else:
                                record['tags'] = value
                    elif key == 'remove_tag':
                        current_tags = record.get('tags', '').split(',')
                        if value in current_tags:
                            current_tags.remove(value)
                            record['tags'] = ','.join(current_tags)
                    elif key == 'national_id':
                        if DataValidator.validate_national_id(value)[0]:
                            record['national_id'] = value
                    elif key == 'phone':
                        if DataValidator.validate_iranian_phone(value)[0]:
                            record['phone'] = value
                
                updated.append(record)
            else:
                unchanged.append(record)
        
        if dry_run:
            return {
                'matched': len(updated),
                'records': updated
            }
        
        save_records(records)
        log(f"BULK_UPDATE: updated {len(updated)} records")
        return len(updated)
    
    @staticmethod
    def export_selected(record_ids, format='csv'):
        """
        خروجی گرفتن از رکوردهای مشخص
        """
        records = load_records()
        selected = [r for r in records if r['id'] in record_ids]
        
        if format == 'csv':
            import csv
            import os
            from core.utils import DATA_DIR
            
            filename = f"bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(DATA_DIR, 'exports', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=selected[0].keys() if selected else [])
                writer.writeheader()
                writer.writerows(selected)
            
            return filepath
        
        return None
    
    @staticmethod
    def copy_records(record_ids, modifications=None):
        """
        کپی کردن رکوردها با تغییرات
        """
        records = load_records()
        new_records = []
        
        for record in records:
            if record['id'] in record_ids:
                import copy
                import uuid
                
                new_record = copy.deepcopy(record)
                new_record['id'] = str(uuid.uuid4())[:8].upper()
                new_record['created_at'] = datetime.now().isoformat()
                
                # اعمال تغییرات
                if modifications:
                    for key, value in modifications.items():
                        if key in new_record:
                            new_record[key] = value
                
                new_records.append(new_record)
        
        records.extend(new_records)
        save_records(records)
        
        return [r['id'] for r in new_records]