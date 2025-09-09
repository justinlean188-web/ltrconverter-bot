"""
API Wrapper for Kivy App
Simplified version of api.py for mobile app usage
"""
import re
import json
import time
import uuid
import threading
from collections import OrderedDict
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from functools import wraps

# Import parsing functions from original api.py
from api import (
    parse_input, normalize_input, get_next_time, map_post_code,
    KH_TIMES, VN_TIMES, USA_TIMES
)

# Global variables that will be set by the Kivy app
BOT_TOKEN = ""
CHAT_ID = ""

# Command queue
command_queue = {}
INCOMPLETE_BETS_LIST = []

def add_command_to_queue(command_data):
    """Add command to queue with unique ID"""
    global command_queue
    command_id = str(uuid.uuid4())
    command_queue[command_id] = {
        "command": command_data,
        "timestamp": time.time(),
        "status": "pending"
    }
    return command_id

def api_response(success=True, message="", data=None, status_code=200):
    """Standardized API response"""
    response = {
        "success": success,
        "message": message,
        "timestamp": time.time(),
        "data": data if data is not None else {}
    }
    return jsonify(response), status_code

def validate_json_request(f):
    """Decorator to validate JSON requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return api_response(False, "Request must be JSON", status_code=400)
        return f(*args, **kwargs)
    return decorated_function

def handle_api_errors(f):
    """Decorator to handle API errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return api_response(False, f"Invalid data: {str(e)}", status_code=400)
        except KeyError as e:
            return api_response(False, f"Missing required field: {str(e)}", status_code=400)
        except Exception as e:
            return api_response(False, f"Internal server error: {str(e)}", status_code=500)
    return decorated_function

# Flask app
app = Flask(__name__)

@app.route("/send_command", methods=['POST'])
@validate_json_request
@handle_api_errors
def send_command():
    """Process betting commands"""
    global INCOMPLETE_BETS_LIST
    
    data = request.json
    if "text" not in data:
        return api_response(False, "Missing required field: text", status_code=400)
    
    raw_text = data['text']
    text = normalize_input(raw_text)
    
    # Initialize variables
    time_types_to_process = []
    name_str = ""
    manual_time_str = ""
    
    # Parse time types
    if "យួន" in text:
        time_types_to_process.append('vn')
    if "ខ្មែរ" in text:
        time_types_to_process.append('kh')
    if "អន្តរជាតិ" in text or "ជាតិ" in text:
        time_types_to_process.append('usa')
    
    lines = text.strip().split('\n')
    first_line_parts = lines[0].strip().split()
    
    # Handle special commands
    if first_line_parts[0].upper() == "SEND":
        command_id = add_command_to_queue({"type": "resend"})
        return api_response(True, "Resend command queued", {"command_id": command_id})
    
    if first_line_parts[0].upper() == "SETUP_BOT":
        command_id = add_command_to_queue({"type": "setup_bot"})
        return api_response(True, "Setup bot command queued", {"command_id": command_id})
    
    if first_line_parts[0].upper() == "CONFIRM" and len(first_line_parts) >= 4:
        invoice_id = first_line_parts[1]
        invoice_name = first_line_parts[2]
        invoice_time_raw = first_line_parts[3].strip()
        
        # Process time
        if invoice_time_raw.lower() == 'vn':
            next_time, _ = get_next_time('vn')
            invoice_time = next_time.replace("AM", "").replace("PM", "").strip()
            time_type = 'vn'
        elif invoice_time_raw.lower() == 'kh':
            next_time, _ = get_next_time('kh')
            invoice_time = next_time.replace("AM", "").replace("PM", "").strip()
            time_type = 'kh'
        elif invoice_time_raw.lower() == 'usa':
            next_time, _ = get_next_time('usa')
            invoice_time = next_time.replace("AM", "").replace("PM", "").replace(":00", "").strip()
            time_type = 'usa'
        else:
            invoice_time = invoice_time_raw.replace("AM", "").replace("PM", "").strip()
            time_type = 'unknown'
        
        command_id = add_command_to_queue({
            "type": "confirm", 
            "id": invoice_id, 
            "name": invoice_name, 
            "time": invoice_time, 
            "time_type": time_type
        })
        return api_response(True, "Confirm command queued", {"command_id": command_id})
    
    # Determine fallback time types
    if not time_types_to_process:
        if len(first_line_parts) > 0 and first_line_parts[0].lower() == "usa":
            time_types_to_process.append("usa")
            name_str = first_line_parts[1] if len(first_line_parts) > 1 else ""
        elif len(first_line_parts) > 0 and first_line_parts[0].lower() in ("kh", "vn"):
            time_types_to_process.append(first_line_parts[0].lower())
            name_str = first_line_parts[1] if len(first_line_parts) > 1 else ""
        elif len(first_line_parts) > 0 and re.match(r"\d{1,2}:\d{2}", first_line_parts[0]):
            time_types_to_process.append("vn_manual")
            manual_time_str = first_line_parts[0].replace("AM", "").replace("PM", "").strip()
            name_str = first_line_parts[1] if len(first_line_parts) > 1 else ""
        else:
            time_types_to_process.append("vn")
            name_str = first_line_parts[0] if len(first_line_parts) > 0 and not any(char.isdigit() for char in first_line_parts[0]) else ""
    else:
        for part in first_line_parts:
            if part.lower() not in ["ខ្មែរ", "យួន", "អន្តរជាតិ", "ជាតិ", "kh", "vn", "usa", "fast"] and not re.match(r"\d{1,2}:\d{2}", part):
                name_str = part
                break
    
    # Process betting data
    INCOMPLETE_BETS_LIST.clear()
    
    multiplier = 1
    if any("x100" in part.lower() for part in first_line_parts):
        multiplier = 100
    
    post_lines = lines[1:]
    if post_lines and any(char.isdigit() for char in post_lines[0]):
        post_lines.insert(0, "ABCD")
    elif not post_lines and any(char.isdigit() for char in lines[0]):
        post_lines = ["ABCD"] + lines[1:]
    elif not post_lines:
        post_lines = ["ABCD"]
    
    post_aliases = {
        "4": "ABCD", "4p": "ABCD", "4*": "ABCD", "*4": "ABCD",
        "4+": "ABCD", "4post": "ABCD", "+4": "ABCD", "lo": "L"
    }
    
    data_list = []
    current_post = None
    last_money = None
    
    for line in post_lines:
        raw_line = line.strip()
        if not raw_line:
            continue
        
        alias = post_aliases.get(raw_line.lower())
        if alias:
            current_post = alias
            continue
        
        if not any(char.isdigit() for char in raw_line) and "ដល" not in raw_line:
            current_post = raw_line.upper().replace(' ', '')
            continue
        
        if current_post:
            bet_line = raw_line.replace("O", "0").replace("o", "0")
            if time_types_to_process[0] == "vn_manual":
                command_time = manual_time_str
            else:
                next_time, _ = get_next_time(time_types_to_process[0])
                command_time = next_time.replace("AM", "").replace("PM", "").strip()
            
            mapped_post = map_post_code(current_post, command_time)
            full_line = f"{mapped_post} {bet_line}"
            parsed = parse_input(full_line)
            
            if parsed:
                bets_to_process = parsed if isinstance(parsed, list) else [parsed]
                
                for p in bets_to_process:
                    p = normalize_input(p)
                    
                    if p.get("Money") and p["Money"].isdigit():
                        current_money = str(int(p["Money"]) * multiplier)
                        p["Money"] = current_money
                        last_money = current_money
                    else:
                        if last_money:
                            p["Money"] = last_money
                        else:
                            bet_str = ""
                            if "Number1" in p:
                                bet_str = f"{p['Number1']}{p.get('Operator', '')}{p.get('Number2', '')}"
                            else:
                                bet_str = f"{p['Number']}{p.get('Operator', '')}"
                            INCOMPLETE_BETS_LIST.append(bet_str)
                    
                    data_list.append(p)
    
    # Group data by post
    data_by_post = OrderedDict()
    for item in data_list:
        post_key = item['Post']
        if post_key not in data_by_post:
            data_by_post[post_key] = []
        data_by_post[post_key].append(item)
    
    # Re-order posts (L last)
    sorted_posts = OrderedDict()
    for post, bets in data_by_post.items():
        if post.upper() != 'L':
            sorted_posts[post] = bets
    if 'L' in data_by_post:
        sorted_posts['L'] = data_by_post['L']
    
    # Build final structure
    final_grouped_data = OrderedDict()
    for post, bets in sorted_posts.items():
        if not bets:
            continue
        final_grouped_data[post] = []
        current_money_group = None
        for bet in bets:
            bet.pop("Post", None)
            money_val = bet.pop("Money", None)
            if current_money_group is None or current_money_group['money'] != money_val:
                new_group = OrderedDict([('money', money_val), ('bets', [bet])])
                final_grouped_data[post].append(new_group)
                current_money_group = new_group
            else:
                current_money_group['bets'].append(bet)
    
    # Create commands
    commands_created = 0
    if final_grouped_data:
        for time_type in time_types_to_process:
            if time_type == "vn_manual":
                time_str = manual_time_str
            else:
                next_time, _ = get_next_time(time_type)
                time_str = next_time.replace("AM", "").replace("PM", "").strip()
                if time_type == 'usa' and time_str.endswith(":00"):
                    time_str = time_str[:-3]
            
            final_command = {
                "name": name_str,
                "time": time_str,
                "data": final_grouped_data
            }
            command_id = add_command_to_queue(final_command)
            commands_created += 1
    
    return api_response(
        True,
        "Command processed successfully",
        {
            "processed_text": text,
            "commands_created": commands_created,
            "time_types": time_types_to_process,
            "incomplete_bets": len(INCOMPLETE_BETS_LIST),
            "incomplete_bet_numbers": INCOMPLETE_BETS_LIST if INCOMPLETE_BETS_LIST else []
        }
    )

@app.route("/get_command", methods=['GET'])
@handle_api_errors
def get_red_command():
    """Get pending commands"""
    global command_queue
    
    pending_commands = {}
    total_pending = 0
    
    for cmd_id, cmd_data in command_queue.items():
        if cmd_data["status"] == "pending":
            pending_commands[cmd_id] = {
                "command": cmd_data["command"],
                "timestamp": cmd_data["timestamp"],
                "age_seconds": time.time() - cmd_data["timestamp"]
            }
            total_pending += 1
    
    return api_response(
        True,
        f"Found {total_pending} pending commands",
        {
            "commands": pending_commands,
            "total_pending": total_pending,
            "queue_size": len(command_queue)
        }
    )

@app.route("/clear_command", methods=['POST'])
@validate_json_request
@handle_api_errors
def clear_command():
    """Clear commands"""
    global command_queue
    
    data = request.json
    
    if data.get("clear_all"):
        cleared_count = len(command_queue)
        command_queue.clear()
        return api_response(True, "All commands cleared", {"cleared_count": cleared_count})
    
    command_ids = data.get("command_ids", [])
    if not command_ids:
        return api_response(False, "No command_ids provided", status_code=400)
    
    cleared_count = 0
    not_found_ids = []
    
    for cmd_id in command_ids:
        if cmd_id in command_queue:
            del command_queue[cmd_id]
            cleared_count += 1
        else:
            not_found_ids.append(cmd_id)
    
    return api_response(
        True,
        f"Cleared {cleared_count} commands",
        {
            "cleared_count": cleared_count,
            "requested_count": len(command_ids),
            "not_found_ids": not_found_ids
        }
    )

@app.route("/task_complete", methods=['GET', 'POST'])
@handle_api_errors
def task_complete():
    """Task completion endpoint"""
    global INCOMPLETE_BETS_LIST
    
    message_text = "✅កត់រួចហើយ"
    incomplete_bets_detected = bool(INCOMPLETE_BETS_LIST)
    
    if INCOMPLETE_BETS_LIST:
        problem_numbers_str = ", ".join(INCOMPLETE_BETS_LIST)
        warning_text = (
            f"‼️ ការភ្នាល់ខ្លះមិនមានទឹកប្រាក់ទេ។\n"
            f"សូមពិនិត្យលេខ: **{problem_numbers_str}**"
        )
        message_text = f"{message_text}\n\n{warning_text}"
        incomplete_bet_list = INCOMPLETE_BETS_LIST.copy()
        INCOMPLETE_BETS_LIST.clear()
    else:
        incomplete_bet_list = []
    
    return api_response(
        True,
        "Task completion processed",
        {
            "incomplete_bets_detected": incomplete_bets_detected,
            "incomplete_bets": incomplete_bet_list,
            "completion_timestamp": time.time()
        }
    )

@app.route("/health", methods=['GET'])
@handle_api_errors
def health_check():
    """Health check endpoint"""
    return api_response(
        True,
        "API is healthy and operational",
        {
            "status": "healthy",
            "queue_size": len(command_queue),
            "pending_commands": sum(1 for cmd in command_queue.values() if cmd["status"] == "pending"),
            "api_version": "2.0"
        }
    )

def start_flask_server(host='0.0.0.0', port=5001, debug=False):
    """Start Flask server in a separate thread"""
    app.run(host=host, port=port, debug=debug, use_reloader=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
