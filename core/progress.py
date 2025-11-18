# core/progress.py
import time
import sys
import random

class AdvancedProgressBar:
    def __init__(self, total=100, prefix='', suffix='', length=30, fill='█', style='modern'):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.fill = fill
        self.style = style
        self.current = 0
        self.start_time = time.time()
        
        self.styles = {
            'modern': '█',
            'classic': '=',
            'dots': '▪',
            'blocks': '▓',
            'arrows': '»'
        }
        
        if style in self.styles:
            self.fill = self.styles[style]
    
    def update(self, progress):
        self.current = progress
        percent = ("{0:.1f}").format(100 * (progress / float(self.total)))
        
        elapsed_time = time.time() - self.start_time
        if progress > 0:
            eta = (elapsed_time / progress) * (self.total - progress)
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: Calculating..."
        
        filled_length = int(self.length * progress // self.total)
        bar = self.fill * filled_length + ' ' * (self.length - filled_length)
        
        if self.style == 'modern':
            line = f'\r{self.prefix} |{bar}| {percent}% | {self.suffix} | {eta_str}'
        else:
            line = f'\r{self.prefix} [{bar}] {percent}% | {self.suffix}'
        
        sys.stdout.write(line)
        sys.stdout.flush()
        
    def finish(self):
        self.update(self.total)
        elapsed_time = time.time() - self.start_time
        print(f"\nCompleted in {elapsed_time:.2f} seconds")
    
    def finish_with_message(self, message):
        self.update(self.total)
        elapsed_time = time.time() - self.start_time
        print(f"\n✓ {message} ({elapsed_time:.2f}s)")


def simple_loading(operation_name, duration=1.0):
    bar = AdvancedProgressBar(total=100, prefix=operation_name, suffix='Processing', length=25, style='modern')
    steps = 100
    delay = duration / steps
    
    for i in range(steps):
        time.sleep(delay)
        bar.update(i + 1)
    
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()

def animated_login():
    print("\nInitializing secure session...")
    
    steps = [
        "Loading security modules",
        "Validating credentials", 
        "Establishing secure connection",
        "Loading user profile",
        "Finalizing session"
    ]
    
    bar = AdvancedProgressBar(total=100, prefix='AUTH', suffix='', length=25, style='modern')
    
    for i, step in enumerate(steps):
        bar.suffix = step
        for j in range(20):
            bar.update(i * 20 + j)
            time.sleep(0.02)
    
    bar.finish_with_message("Authentication successful")

def loading_operation(operation_name, duration=1.0, style='modern'):
    bar = AdvancedProgressBar(total=100, prefix=operation_name, suffix='Processing', length=25, style=style)
    steps = 100
    delay = duration / steps
    
    for i in range(steps):
        time.sleep(delay)
        
        if i < 25:
            bar.suffix = 'Initializing'
        elif i < 50:
            bar.suffix = 'Processing data'
        elif i < 75:
            bar.suffix = 'Finalizing'
        else:
            bar.suffix = 'Almost done'
            
        bar.update(i + 1)
    
    bar.finish_with_message(f"{operation_name} completed")

def searching_animation(duration=1.0):
    bar = AdvancedProgressBar(total=100, prefix='SEARCH', suffix='Scanning database', length=25, style='dots')
    steps = 100
    delay = duration / steps
    
    search_terms = ['Indexing records', 'Filtering results', 'Ranking matches', 'Compiling data']
    
    for i in range(steps):
        time.sleep(delay)
        
        term_index = (i // 25) % len(search_terms)
        bar.suffix = search_terms[term_index]
            
        bar.update(i + 1)
    
    bar.finish_with_message("Search completed")

def saving_animation(duration=1.0):
    bar = AdvancedProgressBar(total=100, prefix='SAVE', suffix='Encrypting data', length=25, style='blocks')
    steps = 100
    delay = duration / steps
    
    save_steps = ['Validating input', 'Encrypting data', 'Writing to storage', 'Verifying integrity']
    
    for i in range(steps):
        time.sleep(delay)
        
        step_index = (i // 25) % len(save_steps)
        bar.suffix = save_steps[step_index]
            
        bar.update(i + 1)
    
    bar.finish_with_message("Data saved successfully")

def backup_animation(duration=2.0):
    bar = AdvancedProgressBar(total=100, prefix='BACKUP', suffix='Creating snapshot', length=25, style='modern')
    steps = 100
    delay = duration / steps
    
    backup_steps = [
        'Analyzing data',
        'Creating snapshot',
        'Compressing files',
        'Encrypting backup',
        'Verifying integrity'
    ]
    
    for i in range(steps):
        time.sleep(delay)
        
        step_index = (i // 20) % len(backup_steps)
        bar.suffix = backup_steps[step_index]
            
        bar.update(i + 1)
    
    bar.finish_with_message("Backup created successfully")

def report_generation_animation(duration=1.5):
    bar = AdvancedProgressBar(total=100, prefix='REPORT', suffix='Compiling data', length=25, style='arrows')
    steps = 100
    delay = duration / steps
    
    report_steps = [
        'Collecting data',
        'Analyzing metrics',
        'Generating insights',
        'Formatting report',
        'Finalizing output'
    ]
    
    for i in range(steps):
        time.sleep(delay)
        
        step_index = (i // 20) % len(report_steps)
        bar.suffix = report_steps[step_index]
            
        bar.update(i + 1)
    
    bar.finish_with_message("Report generated successfully")

def get_animation_for_command(command, duration=1.0):
    animations = {
        'add': lambda: saving_animation(duration),
        'search': lambda: searching_animation(duration),
        'backup': lambda: backup_animation(duration),
        'export': lambda: saving_animation(duration),
        'report': lambda: report_generation_animation(duration),
        'restore': lambda: backup_animation(duration),
        'autobackup': lambda: backup_animation(duration)
    }
    
    return animations.get(command, lambda: loading_operation(command.upper(), duration))

