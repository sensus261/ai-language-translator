"""XML processing utilities for Fallout 4 XML files."""

import os
import re
import threading
from xml.sax.saxutils import escape, unescape
from services import ai_service

# Global state for XML batch processing
xml_batch_processing = False
xml_batch_stop_requested = False

class XMLProcessor:
    """Handles XML file processing operations for Fallout 4 language files."""
    
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
    
    def find_next_string_entry(self):
        """Find the next <String> entry in the XML file and return its details."""
        try:
            if not os.path.exists(self.input_path):
                return None
            
            with open(self.input_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Look for the first <String> entry
            string_pattern = re.compile(r'(<String[^>]*>.*?</String>)', re.DOTALL)
            match = string_pattern.search(content)
            
            if not match:
                return None
            
            string_entry = match.group(1)
            
            # Extract the source text
            source_match = re.search(r'<Source>(.*?)</Source>', string_entry, re.DOTALL)
            if not source_match:
                return None
            
            source_text = source_match.group(1).strip()
            
            # Extract attributes from the String tag
            string_tag_match = re.search(r'<String([^>]*)>', string_entry)
            attributes = string_tag_match.group(1) if string_tag_match else ''
            
            return {
                'full_entry': string_entry,
                'source_text': unescape(source_text),
                'attributes': attributes,
                'start_pos': match.start(),
                'end_pos': match.end()
            }
            
        except Exception as e:
            print(f"[XML-PROCESSOR] Error finding next XML entry: {str(e)}")
            return None

    def remove_string_entry(self, start_pos, end_pos):
        """Remove a specific XML string entry from the file."""
        try:
            if not os.path.exists(self.input_path):
                return False
            
            with open(self.input_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Remove the entry and any trailing newline
            new_content = content[:start_pos] + content[end_pos:]
            new_content = re.sub(r'\n\s*\n', '\n', new_content)  # Remove extra empty lines
            
            with open(self.input_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"[XML-PROCESSOR] Error removing XML entry: {str(e)}")
            return False

    def append_string_entry(self, attributes, source_text, dest_text):
        """Append a translated XML string entry to the output file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # Check if file exists and has proper structure
            if not os.path.exists(self.output_path):
                # Create new XML file with proper structure
                xml_header = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<SSTXMLRessources>
  <Params>
    <Addon>Fallout4</Addon>
    <Source>en</Source>
    <Dest>ro</Dest>
    <Version>2</Version>
  </Params>
  <Content>
  </Content>
</SSTXMLRessources>'''
                with open(self.output_path, 'w', encoding='utf-8') as file:
                    file.write(xml_header)
            
            # Read current content
            with open(self.output_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Prepare the new string entry
            escaped_source = escape(source_text)
            escaped_dest = escape(dest_text)
            
            new_entry = f'''    <String{attributes}>
      <Source>{escaped_source}</Source>
      <Dest>{escaped_dest}</Dest>
    </String>'''
            
            # Find the </Content> tag and insert before it
            content_end_pos = content.find('  </Content>')
            if content_end_pos != -1:
                new_content = content[:content_end_pos] + new_entry + '\n' + content[content_end_pos:]
                
                with open(self.output_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                return True
            
            return False
            
        except Exception as e:
            print(f"[XML-PROCESSOR] Error appending XML entry: {str(e)}")
            return False

    def count_string_entries(self, file_path=None):
        """Count the number of <String> entries in an XML file."""
        try:
            path = file_path or self.input_path
            if not os.path.exists(path):
                return 0
            
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Count <String> entries
            string_pattern = re.compile(r'<String[^>]*>', re.DOTALL)
            matches = string_pattern.findall(content)
            
            return len(matches)
            
        except Exception as e:
            print(f"[XML-PROCESSOR] Error counting XML entries: {str(e)}")
            return 0

    def get_status(self):
        """Get the current status of XML translation files."""
        global xml_batch_processing
        
        input_exists = os.path.exists(self.input_path)
        output_exists = os.path.exists(self.output_path)
        
        entries_remaining = self.count_string_entries(self.input_path) if input_exists else 0
        entries_translated = self.count_string_entries(self.output_path) if output_exists else 0
        
        return {
            "input_file_path": self.input_path,
            "input_file_exists": input_exists,
            "lines_remaining": entries_remaining,
            "output_file_path": self.output_path,
            "output_file_exists": output_exists,
            "lines_translated": entries_translated,
            "batch_processing_status": xml_batch_processing
        }

    def process_next_entry(self):
        """Process the next XML entry."""
        global xml_batch_processing
        
        # Check if batch processing is running
        if xml_batch_processing:
            return {
                "status": "error",
                "error": "Batch processing is currently running",
                "details": "Please wait for batch processing to complete or stop it before processing individual entries."
            }
        
        xml_entry = self.find_next_string_entry()
        
        if xml_entry is None:
            return {"status": "completed", "message": "No more XML entries to process"}
        
        source_text = xml_entry['source_text']
        
        if not source_text.strip():  # Empty source
            # Remove the empty entry and add to output with empty translation
            self.remove_string_entry(xml_entry['start_pos'], xml_entry['end_pos'])
            self.append_string_entry(xml_entry['attributes'], source_text, source_text)
            return {"status": "skipped", "message": "Skipped empty XML entry"}
        
        # Translate the text
        romanian_text = ai_service.translate_text(source_text)
        
        if romanian_text is None:
            return {"status": "error", "error": "XML translation failed", "input": source_text}
        
        print(f"[XML-PROCESSOR] Translation: {romanian_text}")
        
        # Append to output XML file
        if not self.append_string_entry(xml_entry['attributes'], source_text, romanian_text):
            return {"status": "error", "error": "Failed to write to XML output file"}
        
        # Remove the processed entry from input file
        if not self.remove_string_entry(xml_entry['start_pos'], xml_entry['end_pos']):
            return {"status": "error", "error": "Failed to remove processed XML entry from input file"}
        
        return {
            "status": "success",
            "input": source_text,
            "output": romanian_text,
            "input_file_path": self.input_path,
            "output_file_path": self.output_path
        }

    def start_batch_processing(self):
        """Start processing all XML entries in background."""
        global xml_batch_processing, xml_batch_stop_requested
        
        # Check if batch processing is already running
        if xml_batch_processing:
            return {
                "status": "error",
                "error": "Batch processing already in progress",
                "details": "Please wait for the current batch processing to complete before starting a new one."
            }
        
        # Count remaining entries for user info
        remaining_entries = self.count_string_entries()
        
        if remaining_entries == 0:
            return {"status": "completed", "message": "No XML entries found to process."}
        
        # Set the flags to indicate batch processing is starting
        xml_batch_processing = True
        xml_batch_stop_requested = False
        
        # Start the background processing thread
        processing_thread = threading.Thread(target=self._process_all_entries_background)
        processing_thread.daemon = True  # Thread will die when main program exits
        processing_thread.start()
        
        return {
            "status": "success",
            "message": f"Batch processing started successfully! Processing {remaining_entries} XML entries in the background.",
            "entries_to_process": remaining_entries
        }

    def stop_batch_processing(self):
        """Stop the running XML batch processing."""
        global xml_batch_processing, xml_batch_stop_requested
        
        if not xml_batch_processing:
            return {
                "status": "error",
                "error": "No batch processing is currently running",
                "details": "There is no active batch processing to stop."
            }
        
        # Set the stop flag
        xml_batch_stop_requested = True
        
        return {
            "status": "success",
            "message": "Stop request sent. The batch processing will stop after completing the current entry."
        }

    def _process_all_entries_background(self):
        """Background function to process all XML entries."""
        global xml_batch_processing, xml_batch_stop_requested
        
        try:
            processed_count = 0
            skipped_count = 0
            errors = []
            
            print(f"[XML-PROCESSOR] Starting background batch processing...")
            
            while True:
                # Check if stop was requested
                if xml_batch_stop_requested:
                    print(f"[XML-PROCESSOR] Batch processing stopped by user request after {processed_count} entries")
                    break
                
                xml_entry = self.find_next_string_entry()
                
                if xml_entry is None:
                    print(f"[XML-PROCESSOR] Batch processing completed - no more entries found")
                    break  # No more entries
                
                source_text = xml_entry['source_text']
                
                if not source_text.strip():  # Empty entry
                    self.remove_string_entry(xml_entry['start_pos'], xml_entry['end_pos'])
                    self.append_string_entry(xml_entry['attributes'], source_text, source_text)
                    skipped_count += 1
                    continue
                
                # Translate the text
                romanian_text = ai_service.translate_text(source_text)
                
                if romanian_text is None:
                    errors.append(f"Translation failed for: {source_text}")
                    self.remove_string_entry(xml_entry['start_pos'], xml_entry['end_pos'])
                    continue
                
                # Append to output XML file
                if not self.append_string_entry(xml_entry['attributes'], source_text, romanian_text):
                    errors.append(f"Failed to write translation for: {source_text}")
                    continue
                
                # Remove the processed entry from input file
                if not self.remove_string_entry(xml_entry['start_pos'], xml_entry['end_pos']):
                    errors.append(f"Failed to remove processed XML entry: {source_text}")
                    break
                
                processed_count += 1
                
                # Log progress every 100 entries
                if processed_count % 100 == 0:
                    print(f"[XML-PROCESSOR] Progress: {processed_count} XML entries processed")
            
            print(f"[XML-PROCESSOR] Background batch processing finished. Processed: {processed_count}, Skipped: {skipped_count}, Errors: {len(errors)}")
            
        except Exception as e:
            print(f"[XML-PROCESSOR] Error in background batch processing: {str(e)}")
        
        finally:
            # Always reset the flags when processing is done
            xml_batch_processing = False
            xml_batch_stop_requested = False
            print(f"[XML-PROCESSOR] Background batch processing flags reset")

def get_batch_processing_status():
    """Get current batch processing status."""
    global xml_batch_processing
    return xml_batch_processing
